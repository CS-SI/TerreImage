/*=========================================================================

  Program:   ORFEO Toolbox
  Language:  C++
  Date:      $Date$
  Version:   $Revision$


  Copyright (c) Centre National d'Etudes Spatiales. All rights reserved.
  See OTBCopyright.txt for details.


     This software is distributed WITHOUT ANY WARRANTY; without even
     the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR
     PURPOSE.  See the above copyright notices for more information.

=========================================================================*/
#include "otbVectorData.h"
#include "otbVectorDataFileReader.h"
#include "otbVectorDataFileWriter.h"

#include "otbVectorImage.h"
#include "otbImageFileReader.h"

#include "otbOGRDataSourceWrapper.h"

#include "otbImageToEnvelopeVectorDataFilter.h"

#include "otbGeometriesProjectionFilter.h"
#include "otbGeometriesSet.h"

typedef otb::VectorData<> VectorDataType;
typedef otb::VectorDataFileReader<VectorDataType> VectorDataFileReaderType;
typedef otb::VectorDataFileWriter<VectorDataType> VectorDataFileWriterType;

typedef double PixelType;
typedef otb::VectorImage<PixelType> ImageType;
typedef otb::ImageFileReader<ImageType> ImageFileReaderType;

typedef otb::ImageToEnvelopeVectorDataFilter<ImageType, VectorDataType> EnvelopeFilterType;

int ReprojectVector(const char* inputVectorFileName,
                    const char* inputImageFileName,
                    const char* outputVectorFileName)
{

  // Software Guide : BeginLatex
  //
  // Declare the geometries type that you would like to use in your
  // application. Unlike \doxygen{otb}{VectorData}, \doxygen{otb}{GeometriesSet}
  // is a single type for any kind of geometries set (OGR data source, or OGR
  // layer).
  //
  // Software Guide : EndLatex

  // Software Guide : BeginCodeSnippet
  typedef otb::GeometriesSet InputGeometriesType;
  typedef otb::GeometriesSet OutputGeometriesType;
  // Software Guide : EndCodeSnippet

  // Software Guide : BeginLatex
  //
  // First, declare and instantiate the data source
  // \subdoxygen{otb}{ogr}{DataSource}. Then, encapsulate this data source into
  // a \doxygen{otb}{GeometriesSet}.
  //
  // Software Guide : EndLatex

  // Software Guide : BeginCodeSnippet
  otb::ogr::DataSource::Pointer input = otb::ogr::DataSource::New(
    inputVectorFileName, otb::ogr::DataSource::Modes::Read);
  InputGeometriesType::Pointer in_set = InputGeometriesType::New(input);
  // Software Guide : EndCodeSnippet

  // Software Guide : BeginLatex
  //
  // We need the image only to retrieve its projection information,
  // i.e. map projection or sensor model parameters. Hence, the image
  // pixels won't be read, only the header information using the
  // \code{UpdateOutputInformation()} method.
  //
  // Software Guide : EndLatex

  // Software Guide : BeginCodeSnippet
  ImageFileReaderType::Pointer imageReader = ImageFileReaderType::New();
  imageReader->SetFileName(inputImageFileName);
  imageReader->UpdateOutputInformation();
  // Software Guide : EndCodeSnippet

  // Software Guide : BeginLatex
  //
  // The \doxygen{otb}{GeometriesProjectionFilter} will do the work of
  // converting the geometries coordinates. It is usually a good idea
  // to use it when you design applications reading or saving vector
  // data.
  //
  // Software Guide : EndLatex

  // Software Guide : BeginCodeSnippet
  typedef otb::GeometriesProjectionFilter GeometriesFilterType;
  GeometriesFilterType::Pointer filter = GeometriesFilterType::New();
  // Software Guide : EndCodeSnippet

  // Software Guide : BeginLatex
  //
  // Information concerning the original projection of the vector data
  // will be automatically retrieved from the metadata. Nothing else
  // is needed from you:
  //
  // Software Guide : EndLatex

  // Software Guide : BeginCodeSnippet
  filter->SetInput(in_set);
  // Software Guide : EndCodeSnippet

  // Software Guide : BeginLatex
  //
  // Information about the target projection is retrieved directly from
  // the image:
  //
  // Software Guide : EndLatex

  // Software Guide : BeginCodeSnippet
  // necessary for sensors
  //filter->SetOutputKeywordList(imageReader->GetOutput()->GetImageKeywordlist());
  // necessary for sensors
  //filter->SetOutputOrigin(imageReader->GetOutput()->GetOrigin());
  // necessary for sensors
  //filter->SetOutputSpacing(imageReader->GetOutput()->GetSpacing());
  // ~ wkt
  filter->SetOutputProjectionRef( imageReader->GetOutput()->GetProjectionRef() );
  // Software Guide : EndCodeSnippet

  // Software Guide : BeginLatex
  //
  // Finally, the result is saved into a new vector file.
  // Unlike other OTB filters, \doxygen{otb}{GeometriesProjectionFilter} expects
  // to be given a valid output geometries set where to store the result of its
  // processing -- otherwise the result will be an in-memory data source, and
  // not stored in a file nor a data base.
  //
  // Then, the processing is started by calling \code{Update()}. The actual
  // serialization of the results is guaranteed to be completed when the ouput
  // geometries set object goes out of scope, or when \code{SyncToDisk} is
  // called.
  //
  // Software Guide : EndLatex

  // Software Guide : BeginCodeSnippet
  otb::ogr::DataSource::Pointer output = otb::ogr::DataSource::New(
    outputVectorFileName, otb::ogr::DataSource::Modes::Overwrite);
  OutputGeometriesType::Pointer out_set = OutputGeometriesType::New(output);

  filter->SetOutput(out_set);
  filter->Update();
  // Software Guide : EndCodeSnippet

  // Software Guide : BeginLatex
  //
  // Once again, it is worth noting that none of this code is specific to the
  // vector data format. Whether you pass a shapefile, or a KML file, the
  // correct driver will be automatically instantiated.
  //
  // Software Guide : EndLatex

  return EXIT_SUCCESS;
}

int GenerateEnveloppe(const char* inputImageFileName, const char* outputImageEnveloppe)
{
  ImageFileReaderType::Pointer imageReader = ImageFileReaderType::New();
  imageReader->SetFileName(inputImageFileName);
  imageReader->UpdateOutputInformation();
  
  EnvelopeFilterType::Pointer envelope = EnvelopeFilterType::New();
  envelope->SetInput(imageReader->GetOutput());
  envelope->SetSamplingRate(0); // only corners
  envelope->SetOutputProjectionRef(imageReader->GetOutput()->GetProjectionRef());
  envelope->Update();
  
  VectorDataFileWriterType::Pointer writer = VectorDataFileWriterType::New();
  writer->SetFileName(outputImageEnveloppe);
  writer->SetInput(envelope->GetOutput());
  writer->Update();
  
  return EXIT_SUCCESS;
}

int IntersectLayers(const char* inputVector,
                    const char* imageEnveloppe,
                    const char* outputVector )
{
  otb::ogr::DataSource::Pointer inDS;
  inDS = otb::ogr::DataSource::New(inputVector, otb::ogr::DataSource::Modes::Read);
  otb::ogr::Layer vlayer = inDS->GetLayer(0);
  
  otb::ogr::DataSource::Pointer inEnvDS;
  inEnvDS = otb::ogr::DataSource::New(imageEnveloppe, otb::ogr::DataSource::Modes::Read);
  otb::ogr::Layer enveloppeLayer = inEnvDS->GetLayer(0);
  
  otb::ogr::DataSource::Pointer outDS;
  outDS = otb::ogr::DataSource::New(outputVector, otb::ogr::DataSource::Modes::Overwrite);
  OGRSpatialReference oSRS(vlayer.GetProjectionRef().c_str());
  otb::ogr::Layer outLayer = outDS->CreateLayer(vlayer.GetName(), &oSRS, vlayer.GetGeomType());

  for(otb::ogr::Layer::const_iterator featIt1 = enveloppeLayer.begin();
      featIt1!=enveloppeLayer.end();
      ++featIt1) // should be just one iteration
  {
      vlayer.SetSpatialFilter( featIt1->GetGeometry() );
      for(otb::ogr::Layer::const_iterator featIt2 = vlayer.begin();
          featIt2!=vlayer.end();
          ++featIt2)
      {
          //TODO: test if the two polygons overlaps or if they just touch themselves.
          otb::ogr::UniqueGeometryPtr tmp = otb::ogr::Intersection(*(featIt1->GetGeometry()), *(featIt2->GetGeometry()));

          //intersection must be in the same geometry type as the input geometry
          //assert(tmp.get()->getGeometryType() == (*featIt1).GetGeometry()->getGeometryType());
          
          if (tmp.get()->getGeometryType() == wkbPolygon)
            {
            //create the feature in the output layer
            otb::ogr::Feature tmpFeat(outLayer.GetLayerDefn());
            tmpFeat.SetFrom((*featIt1)); // copy fields
            tmpFeat.SetGeometry( tmp.get() );
            outLayer.CreateFeature(tmpFeat);
            }
          else if (tmp.get()->getGeometryType() == wkbMultiPolygon)
            {
            OGRMultiPolygon * collection = static_cast<OGRMultiPolygon *>(tmp.get());
            unsigned int nbGeom = collection->getNumGeometries();
            for(unsigned int c = 0; c < nbGeom; c++)
              {
              otb::ogr::Feature tmpFeat(outLayer.GetLayerDefn());
              tmpFeat.SetFrom((*featIt1)); // copy fields
              tmpFeat.SetGeometry( collection->getGeometryRef(c) );
              outLayer.CreateFeature(tmpFeat);
              }
            }
      }
  }
  return EXIT_SUCCESS;
}

int main(int argc, char * argv[])
{
  if (argc < 6)
    {
    std::cout << argv[0] << " <input_vector> <input_image> <output_imageenveloppe> <tmp_reprojected_vector> <output_vector>" << std::endl;
    return EXIT_FAILURE;
    }

  const char* inputVectorFileName = argv[1];
  const char* inputImageFileName = argv[2];
  const char* outputImageEnveloppeVector = argv[3];
  const char* tmpReprojectedVector = argv[4];
  const char* outputVectorFileName = argv[5];
  
  int status;

  // Generate a shp file with image enveloppe
  // CRS is the image CRS
  status = GenerateEnveloppe(inputImageFileName, outputImageEnveloppeVector);
  if (status != EXIT_SUCCESS)
    {
    return status;
    }
 
  // Reproject input vector into image CRS
  status = ReprojectVector(inputVectorFileName,  inputImageFileName, tmpReprojectedVector);
  if (status != EXIT_SUCCESS)
    {
    return status;
    }
  
  // Generate intersection between reprojected input vector and image enveloppe
  status = IntersectLayers(tmpReprojectedVector, outputImageEnveloppeVector, outputVectorFileName);
  if (status != EXIT_SUCCESS)
    {
    return status;
    }

  return EXIT_SUCCESS;
}
