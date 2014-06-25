cmake_minimum_required( VERSION 2.8 )

project( TerreImage )

# Current official TerreImage software version
set( TerreImage_VERSION_MAJOR 2 )
set( TerreImage_VERSION_MINOR 3 )
set( TerreImage_VERSION_PATCH 2 )
set( TerreImage_VERSION_FULL
     "${TerreImage_VERSION_MAJOR}.${TerreImage_VERSION_MINOR}.${TerreImage_VERSION_PATCH}" )

# Get the timestamp of the build configuration process given in
# "YYYY-MM-DD HH:MM:SS TZ" format
#exec_program( date
#              ARGS "'+%Y-%m-%d %H:%M:%S %z'"
#              OUTPUT_VARIABLE BUILD_TIMESTAMP )

# SimplePacked version of the build timestramp
#string( REGEX REPLACE
#        "^(....)-(..)-(..) (..):(..):(..) .*$"
#        "\\1\\2\\3_\\4\\5\\6"
#        PACKED_BUILD_TIMESTAMP
#        ${BUILD_TIMESTAMP} )

# If GCC is used, increase the warning level to its highest value
if( CMAKE_COMPILER_IS_GNUCC )
  add_definitions( "-Wall -Wextra" )
endif( CMAKE_COMPILER_IS_GNUCC )

# If G++ is used, increase the warning level to its highest value
if( CMAKE_COMPILER_IS_GNUCXX )
  add_definitions( "-Wall -Wextra" )
endif( CMAKE_COMPILER_IS_GNUCXX )

# Disable shared libs on win32 plateforms
IF(WIN32)
  # do not build shared lib under windows
  SET(BUILD_SHARED_LIBS OFF)
  MESSAGE(STATUS "Disabling build shared lib option on windows like OS.")
ELSE(WIN32)
  # on other systems, leave the choice to the user
  OPTION(BUILD_SHARED_LIBS "Build TerreImage with shared libraries." ON)
ENDIF(WIN32)

# Link to the Orfeo ToolBox
find_package( OTB )
if( OTB_FOUND )
  include( ${OTB_USE_FILE} )
else( OTB_FOUND )
  message( FATAL_ERROR "OTB not found. Please set OTB_DIR" )
endif( OTB_FOUND )

# Change the default directory for built binaries
set( EXECUTABLE_OUTPUT_PATH ${CMAKE_BINARY_DIR}/bin )

# Change the default directory for built libraries
set( LIBRARY_OUTPUT_PATH ${CMAKE_BINARY_DIR}/lib )

# On Visual Studio 8 MS deprecated C. This removes all 1.276E1265 security
# warnings
IF(WIN32)
    IF(NOT CYGWIN)
      IF(NOT MINGW)
        IF(NOT ITK_ENABLE_VISUAL_STUDIO_DEPRECATED_C_WARNINGS)
          ADD_DEFINITIONS(
            -D_CRT_FAR_MAPPINGS_NO_DEPRECATE
            -D_CRT_IS_WCTYPE_NO_DEPRECATE
            -D_CRT_MANAGED_FP_NO_DEPRECATE
            -D_CRT_NONSTDC_NO_DEPRECATE
            -D_CRT_SECURE_NO_DEPRECATE
            -D_CRT_SECURE_NO_DEPRECATE_GLOBALS
            -D_CRT_SETERRORMODE_BEEP_SLEEP_NO_DEPRECATE
            -D_CRT_TIME_FUNCTIONS_NO_DEPRECATE
            -D_CRT_VCCLRIT_NO_DEPRECATE
            -D_SCL_SECURE_NO_DEPRECATE
            )
        ENDIF(NOT ITK_ENABLE_VISUAL_STUDIO_DEPRECATED_C_WARNINGS)
        
        IF (MSVC)
          ADD_DEFINITIONS(-D_CRT_SECURE_NO_WARNINGS)
          ADD_DEFINITIONS(-D_CRT_NONSTDC_NO_WARNING)
        ENDIF(MSVC)
        
      ENDIF(NOT MINGW)
    ENDIF(NOT CYGWIN)
ENDIF(WIN32)

add_subdirectory(ClassificationSupervisee_cpp)
add_subdirectory(packaging)

