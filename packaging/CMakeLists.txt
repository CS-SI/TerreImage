if(NOT WIN32)
  return()
endif()

find_program(ZIP_EXECUTABLE
             NAMES zip)

find_program(UNZIP_EXECUTABLE
             NAMES unzip)

FILE(TO_CMAKE_PATH "$ENV{GDAL_DATA}" GDAL_DATA)
IF(NOT GDAL_DATA)
  MESSAGE(FATAL_ERROR "GDAL_DATA environment variable is not set. Cannot continue")
ENDIF()

set(PACKAGE_NAME TerreImage)
set(PACKAGE_VERSION_STRING ${TerreImage_VERSION_FULL})


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

get_filename_component(OTB_INSTALL_DIR "${OTB_MODULES_DIR}" PATH)
get_filename_component(OTB_INSTALL_DIR "${OTB_INSTALL_DIR}" PATH)
get_filename_component(OTB_INSTALL_DIR "${OTB_INSTALL_DIR}" PATH)
get_filename_component(OTB_INSTALL_DIR "${OTB_INSTALL_DIR}" PATH)
set(OTB_APPLICATIONS_INSTALL_DIR ${OTB_INSTALL_DIR}/lib/otb/applications)
set(OTB_APPLICATION_LAUNCHER ${OTB_INSTALL_DIR}/bin/otbApplicationLauncherCommandLine)

# get_target_property(FullSVMClassificationChain_OUTPUT_LOCATION
#                     otbapp_FullSVMClassificationChain
#                     LOCATION_RELWITHDEBINFO)
# get_target_property(otbCropVectorDataToImage_OUTPUT_LOCATION
#                     otbCropVectorDataToImage
#                     LOCATION_RELWITHDEBINFO)

set(FullSVMClassificationChain_OUTPUT_LOCATION "$<TARGET_FILE:otbapp_FullSVMClassificationChain>")
set(otbCropVectorDataToImage_OUTPUT_LOCATION "$<TARGET_FILE:otbCropVectorDataToImage>")


add_custom_target(qgis_BundlePlugin
                  ALL
                  COMMENT "Making bundle for QGIS classification plugin")
                  
add_custom_command(TARGET qgis_BundlePlugin PRE_BUILD
                   COMMAND ${CMAKE_COMMAND} -E copy ${FullSVMClassificationChain_OUTPUT_LOCATION} ${BUNDLEDIR}/win32/plugin
                   COMMAND ${CMAKE_COMMAND} -E copy ${otbCropVectorDataToImage_OUTPUT_LOCATION} ${BUNDLEDIR}/win32/bin
                   COMMAND ${CMAKE_COMMAND} -E copy ${OTB_APPLICATIONS_INSTALL_DIR}/otbapp_ConcatenateImages.dll ${BUNDLEDIR}/win32/plugin
                   COMMAND ${CMAKE_COMMAND} -E copy ${OTB_APPLICATIONS_INSTALL_DIR}/otbapp_KMeansClassification.dll ${BUNDLEDIR}/win32/plugin
                   COMMAND ${CMAKE_COMMAND} -E copy ${OTB_APPLICATIONS_INSTALL_DIR}/otbapp_ColorMapping.dll ${BUNDLEDIR}/win32/plugin
                   COMMAND ${CMAKE_COMMAND} -E copy ${OTB_APPLICATIONS_INSTALL_DIR}/otbapp_BandMath.dll ${BUNDLEDIR}/win32/plugin
                   COMMAND ${CMAKE_COMMAND} -E copy ${OTB_APPLICATIONS_INSTALL_DIR}/otbapp_ReadImageInfo.dll ${BUNDLEDIR}/win32/plugin
                   COMMAND ${CMAKE_COMMAND} -E copy ${OTB_APPLICATIONS_INSTALL_DIR}/otbapp_KmzExport.dll ${BUNDLEDIR}/win32/plugin
                   COMMAND ${CMAKE_COMMAND} -E copy ${OTB_APPLICATION_LAUNCHER} ${BUNDLEDIR}/win32/bin
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
                   ${CMAKE_SOURCE_DIR}/img/*.png
                   ${CMAKE_SOURCE_DIR}/metadata.txt
                   ${CMAKE_SOURCE_DIR}/ReleaseNote.txt)
                   
 message("CMAKE_PROJECT_DIR : ${CMAKE_PROJECT_DIR}")

#message("PyFiles : ${PyFiles}")
foreach(f ${PyFiles})
    add_custom_command(TARGET qgis_BundlePlugin PRE_BUILD
                      COMMAND ${CMAKE_COMMAND} -E copy ${f} ${BUNDLEDIR})
endforeach()


if(MSVC)
FILE(TO_CMAKE_PATH "$ENV{OSGEO4W_ROOT}" OSGEO4W_ROOT)
IF(WIN32 AND NOT OSGEO4W_ROOT)
  MESSAGE(FATAL_ERROR "Cannot generate installer without OSGeo4W environment : OSGEO4W_ROOT")
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

add_custom_command(TARGET qgis_BundlePlugin PRE_BUILD
                   COMMAND ${CMAKE_COMMAND} -E copy ${OSGEO4W_ROOT}/bin/msvcrt.dll ${BUNDLEDIR}/win32/bin
                   COMMAND ${CMAKE_COMMAND} -E copy ${OSGEO4W_ROOT}/bin/msvcp60.dll ${BUNDLEDIR}/win32/bin
                   COMMAND ${CMAKE_COMMAND} -E copy ${OSGEO4W_ROOT}/bin/msvcp70.dll ${BUNDLEDIR}/win32/bin
                   COMMAND ${CMAKE_COMMAND} -E copy ${OSGEO4W_ROOT}/bin/msvcp71.dll ${BUNDLEDIR}/win32/bin
                   COMMAND ${CMAKE_COMMAND} -E copy ${OSGEO4W_ROOT}/bin/msvcr71.dll ${BUNDLEDIR}/win32/bin
                   COMMAND ${CMAKE_COMMAND} -E copy ${MSVC10_CRT_DIR}/msvcp100.dll ${BUNDLEDIR}/win32/bin
                   COMMAND ${CMAKE_COMMAND} -E copy ${MSVC10_CRT_DIR}/msvcr100.dll ${BUNDLEDIR}/win32/bin
                   COMMAND ${CMAKE_COMMAND} -E copy ${OSGEO4W_ROOT}/bin/libgcc_s_dw2-1.dll ${BUNDLEDIR}/win32/bin
                   COMMAND ${CMAKE_COMMAND} -E copy ${OSGEO4W_ROOT}/bin/libiconv-2.dll ${BUNDLEDIR}/win32/bin
		   )

add_custom_command(TARGET qgis_BundlePlugin PRE_BUILD
                       COMMAND ${CMAKE_COMMAND}
                          -DBUNDLE:FILEPATH=${BUNDLEDIR}/win32/bin/otbApplicationLauncherCommandLine.exe
                          -DPLUGIN:FILEPATH=${BUNDLEDIR}/win32/plugin/otbapp_FullSVMClassificationChain.dll
                          -P ${CMAKE_CURRENT_SOURCE_DIR}/BundleFixing.cmake
                   COMMAND ${ZIP_EXECUTABLE} -9r ${CMAKE_CURRENT_BINARY_DIR}/${PACKAGE_NAME}.${PACKAGE_VERSION_STRING}.zip ${PLUGIN_NAME})

endif()

if(WIN32 AND CMAKE_CROSSCOMPILING)



#used in PackageHelper.cmake (don't change)
set(PKG_INSTALL_PREFIX "${CMAKE_INSTALL_PREFIX}")

if(NOT MXE_TARGET_DIR)
  message(FATAL_ERROR "MXE_TARGET_DIR is missing")
endif()

##### End of checking required tools and platform. (cross-compile with zip)

#define the name of final archive based on build architecture. win32 or win64?
set(PACKAGE_PLATFORM_NAME win)
if(MXE_TARGET_DIR MATCHES "i686")
  set(MXE_ARCH "i686")
  set(PACKAGE_ARCH "32")
elseif(MXE_TARGET_DIR MATCHES "x86_64")
  set(MXE_ARCH "x86_64")
  set(PACKAGE_ARCH "64") #helper for ARCHIVE_NAME
endif()

get_filename_component(MXE_MXEROOT ${MXE_TARGET_DIR} PATH)
get_filename_component(MXE_MXEROOT ${MXE_MXEROOT} PATH)

message( "-- Configuring package")
set(PACKAGE_PROJECT_DIR ${CMAKE_BINARY_DIR}/PACKAGE)
execute_process(COMMAND ${CMAKE_COMMAND} -E make_directory "${PACKAGE_PROJECT_DIR}/_build")
#Easy way to have the write "PACKAGE_PROJECT_DIR/src/PACKAGE-${PACKAGE}/CMakeLists.txt"
#inside foreach()

set(ARCHIVE_NAME ${PACKAGE_NAME}-${PACKAGE_VERSION_STRING}-${PACKAGE_PLATFORM_NAME}${PACKAGE_ARCH})

#empty build directory
execute_process(COMMAND ${CMAKE_COMMAND} -E remove_directory "${PKG_INSTALL_PREFIX}/${ARCHIVE_NAME}")

file(WRITE "${PACKAGE_PROJECT_DIR}/CMakeLists.txt"
  "cmake_minimum_required(VERSION 2.6)
       include(CMakeParseArguments)
       include(CMakeDetermineSystem)
       set(Monteverdi_SOURCE_DIR \"${Monteverdi_SOURCE_DIR}\")
       set(PACKAGE_SUPPORT_FILES_DIR \"${Monteverdi_SOURCE_DIR}/Packaging\")
       set(OTB_MODULES_DIR \"${OTB_MODULES_DIR}\")
       set(QT_PLUGINS_DIR \"${QT_PLUGINS_DIR}\")
       set(CMAKE_CROSSCOMPILING ON)
       set(QT_TRANSLATIONS_DIR \"${QT_TRANSLATIONS_DIR}\")
       set(Monteverdi_BINARY_DIR \"${CMAKE_BINARY_DIR}\")
       set(CMAKE_INSTALL_PREFIX \"${CMAKE_INSTALL_PREFIX}\")
       set(Monteverdi_INSTALL_DATA_DIR \"${Monteverdi_INSTALL_DATA_DIR}\")
       set(MXE_ARCH \"${MXE_ARCH}\")
       set(MXE_MXEROOT \"${MXE_MXEROOT}\")
       set(PKG_INSTALL_PREFIX \"${CMAKE_INSTALL_PREFIX}\")
       include(${CMAKE_CURRENT_SOURCE_DIR}/PackageHelper.cmake)
       super_package(STAGE_DIR \"${ARCHIVE_NAME}\")" )

   # add_custom_target(InstallProject
   #   COMMAND ${CMAKE_COMMAND} --build "${CMAKE_BINARY_DIR}" --target install
   #   WORKING_DIRECTORY "${CMAKE_BINARY_DIR}")

   #custom targets to configure , build and create package.
   add_custom_target(configure-package
     COMMAND ${CMAKE_COMMAND}
     "${PACKAGE_PROJECT_DIR}"
     WORKING_DIRECTORY "${PACKAGE_PROJECT_DIR}/_build"
     )

   add_custom_target(build-package
     COMMAND ${CMAKE_COMMAND}
     "--build" "${PACKAGE_PROJECT_DIR}/_build" "--target" "install"
     WORKING_DIRECTORY "${PACKAGE_PROJECT_DIR}/_build"
     DEPENDS configure-package)

   add_custom_target(qgis_BundlePlugin
     COMMAND ${ZIP_EXECUTABLE} "-r" "${CMAKE_BINARY_DIR}/${ARCHIVE_NAME}.zip" "${ARCHIVE_NAME}"
     WORKING_DIRECTORY "${PKG_INSTALL_PREFIX}"
     DEPENDS build-package)

endif()

add_dependencies(qgis_BundlePlugin otbapp_FullSVMClassificationChain otbCropVectorDataToImage)



