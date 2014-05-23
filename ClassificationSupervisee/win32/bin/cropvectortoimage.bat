:::::::::::::::::::::::::::::::::::::::::::::::::::::::::
:: FullSVMClassificationChain launcher to set up proper GDAL environment
:::::::::::::::::::::::::::::::::::::::::::::::::::::::::

:: Get the directory of the current script 
@set CURRENT_SCRIPT_DIR=%~dp0

:: Set GDAL_DATA env. variable
@set GDAL_DATA=%CURRENT_SCRIPT_DIR%..\share\gdal

:: Reset ITK_AUTOLOAD_PATH as it can conflict if some plugins are found
:: but built against other releases
@set ITK_AUTOLOAD_PATH=
:: Reset GDAL_DRIVER_PATH as it can conflict if some plugins are found
:: but built against other releases
@set GDAL_DRIVER_PATH=

:: Start 
"%CURRENT_SCRIPT_DIR%otbCropVectorDataToImage.exe" %*

