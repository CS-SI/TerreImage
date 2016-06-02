#OTB_CREATE_APPLICATION(NAME           FullSVMClassificationChain
#                       SOURCES        otbFullSVMClassificationChain.cxx
#                       LINK_LIBRARIES OTBIO;OTBCommon;OTBBasicFilters;OTBFeatureExtraction;OTBLearning)                                            

add_executable(otbCropVectorDataToImage otbCropVectorDataToImage.cxx)
target_link_libraries(otbCropVectorDataToImage OTBProjection OTBCommon OTBImageIO OTBVectorDataIO)

OTB_CREATE_APPLICATION(NAME           ComputeLabelImagePopulation
                       SOURCES        otbComputeLabelImagePopulation.cxx
                       LINK_LIBRARIES OTBImageIO;OTBCommon;OTBStatistics;OTBTinyXML) 
