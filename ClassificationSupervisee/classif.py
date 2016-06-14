
from osgeo import gdal
import xml.etree.ElementTree as ET
import os
import argparse
#from TerreImage import terre_image_run_process
import terre_image_run_process

def create_vrt_from_filelist(vrt_name, filelist):
    rootNode = ET.Element( 'VRTDataset' )

    for filename in filelist:
        print filename
        ds = gdal.Open(filename)

        print "[ RASTER BAND COUNT ]: ", ds.RasterCount
        for band_number in range( ds.RasterCount ):
            band_number += 1
            bandNode = ET.SubElement( rootNode, "VRTRasterBand", {'band': '1'} )

            sourceNode = ET.SubElement(bandNode, 'SimpleSource')
            node = ET.SubElement(sourceNode, 'SourceFilename', {'relativeToVRT': '1'})
            node.text = filename
            node = ET.SubElement(sourceNode, 'SourceBand')
            node.text = str(band_number)
        
            band = ds.GetRasterBand(band_number)
            dataType = gdal.GetDataTypeName(band.DataType)
            bandNode.attrib['dataType'] = dataType

    ds1 = gdal.Open(filelist[0])
    rootNode.attrib['rasterXSize'] = str(ds1.RasterXSize)
    rootNode.attrib['rasterYSize'] = str(ds1.RasterYSize)

    geotransform = ds.GetGeoTransform()
    ftuple = tuple(map(str, geotransform))
    geotransform = ET.SubElement( rootNode, "GeoTransform")
    geotransform.text = ", ".join(ftuple)  # "0.0, 1.0, 0.0, 0.0, 0.0, -1.0"
    node = ET.SubElement(rootNode, 'SRS')
    node.text = ds.GetProjection() # projection

    stringToReturn = ET.tostring(rootNode)
    print stringToReturn


    #if not os.path.isfile( vrt_name):
    writer = open( vrt_name, 'w')
    writer.write( stringToReturn )
    writer.close()
    
def full_classification(filelist, 
                        vrtfile, 
                        outstatfile, 
                        outsvmfile, 
                        confmat,
                        vd,
                        out,
                        outregul):
    
    app_dir="/usr/bin"
         
    # Merge the input images
    create_vrt_from_filelist(vrtfile, filelist)
    
    #compute stats
    print("----COMPUTE STATS----")
    statlauncher = "%s/otbcli_ComputeImagesStatistics" % app_dir
    statcommand = ('%s'
                   ' -il "%s" '
                   ' -out "%s" '
                   % (statlauncher, vrtfile, outstatfile))
    terre_image_run_process.run_process(statcommand, True)

    # Train images
    print("----TRAIN----")
    trainlauncher = "%s/otbcli_TrainImagesClassifier" % app_dir
    traincommand = ('%s'
                    ' -io.il "%s" '
                    ' -io.vd "%s" '
                    ' -io.imstat "%s" '
                    ' -io.out "%s" '
                    ' -io.confmatout "%s"'
                    ' -classifier rf'
                    ' -sample.vtr 0.1' 
                    % (trainlauncher, vrtfile, vd, outstatfile, outsvmfile, confmat))
    terre_image_run_process.run_process(traincommand, True)

    # Image Classification 
    print("----CLASSIF----")
    classiflauncher="%s/otbcli_ImageClassifier" % app_dir
    classifcommand = ('%s'
                      ' -in "%s" '
                      ' -imstat "%s" '
                      ' -model "%s" '
                      ' -out "%s" '
                      % (classiflauncher, vrtfile, outstatfile, outsvmfile, out))
    terre_image_run_process.run_process(classifcommand, True)

    # Regularization
    print("----REGULARISATION----")
    regullauncher="%s/otbcli_ClassificationMapRegularization" % app_dir
    regulcommand=('%s'
                  ' -io.in "%s" '
                  ' -io.out "%s" '
                  ' -ip.radius 1 '
                  ' -ip.suvbool false '
                  % (regullauncher, out, outregul))
    terre_image_run_process.run_process(regulcommand, True)
    
    #TODO Population stats
    #statpoplauncher=""
    #statpopcmmand=""
    #terre_image_run_process.run_process(statpopcmmand, True)
    
    #TODO ajout de la sauvegarde des parameters
    
if __name__ == '__main__':
    
    parser = argparse.ArgumentParser()
    #parser.add_argument('--filelist', nargs='*', type=argparse.FileType('r'))
    parser.add_argument('--filelist', nargs='*')
    parser.add_argument('--vrtfile')
    parser.add_argument('--outstatfile')
    parser.add_argument('--outsvmfile') 
    parser.add_argument('--confmat')
    parser.add_argument('--vd')
    parser.add_argument('--out')
    parser.add_argument('--outregul')
    args = parser.parse_args()
    
    full_classification(args.filelist, 
                        args.vrtfile, 
                        args.outstatfile, 
                        args.outsvmfile, 
                        args.confmat,
                        args.vd, 
                        args.out, 
                        args.outregul)
