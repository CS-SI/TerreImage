otb_create_application(NAME           ComputeLabelImagePopulation
                       SOURCES        otbComputeLabelImagePopulation.cxx
                       LINK_LIBRARIES   ${OTBImageIO_LIBRARIES} ${OTBStatistics_LIBRARIES} ${OTBTinyXML_LIBRARIES} ${OTBApplicationEngine_LIBRARIES}) 
