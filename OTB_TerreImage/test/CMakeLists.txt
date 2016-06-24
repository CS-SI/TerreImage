otb_module_test()

otb_test_application(NAME   ComputeLabelImagePopulationTest1
                     APP  ComputeLabelImagePopulation
                     OPTIONS -in1 ${INPUTDATA}/Classification/QB_1_ortho_C1.tif
                             -in2 ${INPUTDATA}/Classification/QB_1_ortho_C1.tif
                             -out ${TEMP}/out_stat_pop1.xml)

otb_test_application(NAME   ComputeLabelImagePopulationTest2
                     APP  ComputeLabelImagePopulation
                     OPTIONS -in1 ${INPUTDATA}/Classification/QB_1_ortho.tif
                             -in2 ${INPUTDATA}/Classification/QB_1_ortho_C1.tif
                             -out ${TEMP}/out_stat_pop2.xml)
