if(WIN32)

set(PLUGIN_NAME ${CMAKE_PROJECT_NAME})

set(BUNDLEDIR  ${CMAKE_CURRENT_BINARY_DIR}/${PLUGIN_NAME})
file(MAKE_DIRECTORY ${BUNDLEDIR})
file(MAKE_DIRECTORY ${BUNDLEDIR}/win32)
file(MAKE_DIRECTORY ${BUNDLEDIR}/win32/bin)
file(MAKE_DIRECTORY ${BUNDLEDIR}/win32/plugin)
file(MAKE_DIRECTORY ${BUNDLEDIR}/win32/share/gdal)
file(MAKE_DIRECTORY ${BUNDLEDIR}/ClassificationSupervisee)
file(MAKE_DIRECTORY ${BUNDLEDIR}/DockableMirrorMap)
file(MAKE_DIRECTORY ${BUNDLEDIR}/valuetool)

FILE(TO_CMAKE_PATH "$ENV{OSGEO4W_ROOT}" OSGEO4W_ROOT)
IF(WIN32 AND NOT OSGEO4W_ROOT)
  MESSAGE(FATAL_ERROR "Cannot generate installer without OSGeo4W environment : OSGEO4W_ROOT")
ENDIF()

FILE(TO_CMAKE_PATH "$ENV{GDAL_DATA}" GDAL_DATA)
IF(NOT GDAL_DATA)
  MESSAGE(FATAL_ERROR "Cannot generate installer without OSGeo4W environment : GDAL_DATA")
ENDIF()


# Find MSVC10 redistributable package
set(CMAKE_MSVC_ARCH x86)
file(TO_CMAKE_PATH "$ENV{SYSTEMROOT}" SYSTEMROOT)
get_filename_component(devenv_dir "${CMAKE_MAKE_PROGRAM}" PATH)
get_filename_component(base_dir "${devenv_dir}/../.." ABSOLUTE)
get_filename_component(msvc_install_dir
    "[HKEY_LOCAL_MACHINE\\SOFTWARE\\Microsoft\\VisualStudio\\10.0;InstallDir]" ABSOLUTE)
find_path(MSVC10_REDIST_DIR NAMES ${CMAKE_MSVC_ARCH}/Microsoft.VC100.CRT
    PATHS
    "${msvc_install_dir}/../../VC/redist"
    "${base_dir}/VC/redist"
    "$ENV{ProgramFiles}/Microsoft Visual Studio 10.0/VC/redist"
    "$ENV{ProgramFiles(x86)}/Microsoft Visual Studio 10.0/VC/redist"
    )
mark_as_advanced(MSVC10_REDIST_DIR)
set(MSVC10_CRT_DIR "${MSVC10_REDIST_DIR}/${CMAKE_MSVC_ARCH}/Microsoft.VC100.CRT")




find_program(ZIP_EXECUTABLE
             NAMES zip)

find_program(UNZIP_EXECUTABLE
             NAMES unzip)

get_target_property(FullSVMClassificationChain_OUTPUT_LOCATION
                    otbapp_FullSVMClassificationChain
                    LOCATION_RELWITHDEBINFO)
get_target_property(otbCropVectorDataToImage_OUTPUT_LOCATION
                    otbCropVectorDataToImage
                    LOCATION_RELWITHDEBINFO)

                    
add_custom_target(qgis_BundlePlugin
                  ALL
                  COMMENT "Making bundle for QGIS classification plugin")
                  
add_custom_command(TARGET qgis_BundlePlugin PRE_BUILD
                   COMMAND ${CMAKE_COMMAND} -E copy ${FullSVMClassificationChain_OUTPUT_LOCATION} ${BUNDLEDIR}/win32/plugin
                   COMMAND ${CMAKE_COMMAND} -E copy ${otbCropVectorDataToImage_OUTPUT_LOCATION} ${BUNDLEDIR}/win32/bin
                   COMMAND ${CMAKE_COMMAND} -E copy ${OTB_DIR}/bin/RelWithDebInfo/otbapp_ConcatenateImages.dll ${BUNDLEDIR}/win32/plugin
                   COMMAND ${CMAKE_COMMAND} -E copy ${OTB_DIR}/bin/RelWithDebInfo/otbapp_KMeansClassification.dll ${BUNDLEDIR}/win32/plugin
                   COMMAND ${CMAKE_COMMAND} -E copy ${OTB_DIR}/bin/RelWithDebInfo/otbapp_ColorMapping.dll ${BUNDLEDIR}/win32/plugin
                   COMMAND ${CMAKE_COMMAND} -E copy ${OTB_DIR}/bin/RelWithDebInfo/otbapp_BandMath.dll ${BUNDLEDIR}/win32/plugin
                   COMMAND ${CMAKE_COMMAND} -E copy ${OTB_DIR}/bin/RelWithDebInfo/otbapp_ReadImageInfo.dll ${BUNDLEDIR}/win32/plugin
                   COMMAND ${CMAKE_COMMAND} -E copy ${OTB_DIR}/bin/RelWithDebInfo/otbapp_KmzExport.dll ${BUNDLEDIR}/win32/plugin
                   COMMAND ${CMAKE_COMMAND} -E copy ${OTB_APPLICATION_LAUNCHER} ${BUNDLEDIR}/win32/bin
                   COMMAND ${CMAKE_COMMAND} -E copy ${OSGEO4W_ROOT}/bin/msvcrt.dll ${BUNDLEDIR}/win32/bin
                   COMMAND ${CMAKE_COMMAND} -E copy ${OSGEO4W_ROOT}/bin/msvcp60.dll ${BUNDLEDIR}/win32/bin
                   COMMAND ${CMAKE_COMMAND} -E copy ${OSGEO4W_ROOT}/bin/msvcp70.dll ${BUNDLEDIR}/win32/bin
                   COMMAND ${CMAKE_COMMAND} -E copy ${OSGEO4W_ROOT}/bin/msvcp71.dll ${BUNDLEDIR}/win32/bin
                   COMMAND ${CMAKE_COMMAND} -E copy ${OSGEO4W_ROOT}/bin/msvcr71.dll ${BUNDLEDIR}/win32/bin
                   COMMAND ${CMAKE_COMMAND} -E copy ${MSVC10_CRT_DIR}/msvcp100.dll ${BUNDLEDIR}/win32/bin
                   COMMAND ${CMAKE_COMMAND} -E copy ${MSVC10_CRT_DIR}/msvcr100.dll ${BUNDLEDIR}/win32/bin
                   COMMAND ${CMAKE_COMMAND} -E copy ${OSGEO4W_ROOT}/bin/libgcc_s_dw2-1.dll ${BUNDLEDIR}/win32/bin
                   COMMAND ${CMAKE_COMMAND} -E copy ${OSGEO4W_ROOT}/bin/libiconv-2.dll ${BUNDLEDIR}/win32/bin
                   COMMAND ${CMAKE_COMMAND} -E copy_directory ${GDAL_DATA} ${BUNDLEDIR}/win32/share/gdal
                   COMMAND ${CMAKE_COMMAND} -E copy ${CMAKE_CURRENT_SOURCE_DIR}/cropvectortoimage.bat ${BUNDLEDIR}/win32/bin
                   COMMAND ${CMAKE_COMMAND} -E copy ${CMAKE_CURRENT_SOURCE_DIR}/classification.bat ${BUNDLEDIR}/win32/bin
                   COMMAND ${CMAKE_COMMAND} -E copy ${CMAKE_CURRENT_SOURCE_DIR}/otbcli.bat ${BUNDLEDIR}/win32/bin
                  
                   COMMAND ${CMAKE_COMMAND} -E copy_directory ${CMAKE_SOURCE_DIR}/ClassificationSupervisee ${BUNDLEDIR}/ClassificationSupervisee
                   COMMAND ${CMAKE_COMMAND} -E copy_directory ${CMAKE_SOURCE_DIR}/DockableMirrorMap ${BUNDLEDIR}/DockableMirrorMap
                   COMMAND ${CMAKE_COMMAND} -E copy_directory ${CMAKE_SOURCE_DIR}/valuetool ${BUNDLEDIR}/valuetool
                   )
                   
file(GLOB PyFiles  ${CMAKE_SOURCE_DIR}/*.py
                   ${CMAKE_SOURCE_DIR}/*.ui
                   ${CMAKE_SOURCE_DIR}/*.qrc
                   ${CMAKE_SOURCE_DIR}/*.png
                   ${CMAKE_SOURCE_DIR}/metadata.txt
                   ${CMAKE_SOURCE_DIR}/ReleaseNote.txt)
                   
message("CMAKE_PROJECT_DIR : ${CMAKE_PROJECT_DIR}")
message("PyFiles : ${PyFiles}")
foreach(f ${PyFiles})
    add_custom_command(TARGET qgis_BundlePlugin PRE_BUILD
                       COMMAND ${CMAKE_COMMAND} -E copy ${f} ${BUNDLEDIR})
endforeach()


add_custom_command(TARGET qgis_BundlePlugin PRE_BUILD
                       COMMAND ${CMAKE_COMMAND}
                          -DBUNDLE:FILEPATH=${BUNDLEDIR}/win32/bin/otbApplicationLauncherCommandLine.exe
                          -DPLUGIN:FILEPATH=${BUNDLEDIR}/win32/plugin/otbapp_FullSVMClassificationChain.dll
                          -P ${CMAKE_CURRENT_SOURCE_DIR}/BundleFixing.cmake
                   COMMAND ${ZIP_EXECUTABLE} -9r ${CMAKE_CURRENT_BINARY_DIR}/TerreImage.${TerreImage_VERSION_FULL}.zip ${PLUGIN_NAME})

add_dependencies(qgis_BundlePlugin otbapp_FullSVMClassificationChain otbCropVectorDataToImage)


endif()