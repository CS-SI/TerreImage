OTB_CREATE_APPLICATION(NAME           FullSVMClassificationChain
                       SOURCES        otbFullSVMClassificationChain.cxx
                       LINK_LIBRARIES OTBIO;OTBCommon;OTBBasicFilters;OTBFeatureExtraction;OTBLearning)                                            

add_executable(otbCropVectorDataToImage otbCropVectorDataToImage.cxx)
target_link_libraries(otbCropVectorDataToImage OTBProjection OTBCommon OTBImageIO OTBVectorDataIO)
