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
#include "otbWrapperApplication.h"
#include "otbWrapperApplicationFactory.h"

// Statistics computation
#include "otbStreamingStatisticsVectorImageFilter.h"

// ListSample
#include "itkVariableLengthVector.h"
#include "otbListSampleGenerator.h"

// SVM estimator
#include "otbSVMSampleListModelEstimator.h"

// Validation
#include "otbSVMClassifier.h"
#include "otbConfusionMatrixCalculator.h"

// Normalize the samples
#include "otbShiftScaleSampleListFilter.h"

// List sample concatenation
#include "otbConcatenateSampleListFilter.h"

// TODO : no listsample Balancing done ???
//#include "otbListSampleToBalancedListSampleFilter.h"

// Extract a ROI of the vectordata
#include "otbVectorDataIntoImageProjectionFilter.h"

// Classification
#include "otbSVMImageClassificationFilter.h"
#include "otbShiftScaleVectorImageFilter.h"
#include "otbNeighborhoodMajorityVotingImageFilter.h"

// Concatenate Images
#include "otbImageListToVectorImageFilter.h"
#include "otbMultiToMonoChannelExtractROI.h"
#include "otbImageList.h"
#include "otbObjectList.h"

#include "itkCastImageFilter.h"

#include "otbStreamingHistogramVectorImageFilter.h"
#include "otbTinyXML.h"


namespace otb
{
namespace Wrapper
{

// 
typedef FloatVectorImageType::PixelType PixelType;

// Training vectordata
typedef itk::VariableLengthVector<FloatImageType::PixelType> MeasurementType;

// SampleList manipulation
typedef otb::ListSampleGenerator<FloatVectorImageType, VectorDataType> ListSampleGeneratorType;

typedef ListSampleGeneratorType::ListSampleType ListSampleType;
typedef ListSampleGeneratorType::LabelType LabelType; //FixedArray<int,1>
typedef ListSampleGeneratorType::ListLabelType LabelListSampleType;
typedef otb::Statistics::ConcatenateSampleListFilter<ListSampleType> ConcatenateListSampleFilterType;
typedef otb::Statistics::ConcatenateSampleListFilter<LabelListSampleType> ConcatenateLabelListSampleFilterType;

// reduce and center listSample filter
typedef otb::Statistics::ShiftScaleSampleListFilter<ListSampleType, ListSampleType> ShiftScaleFilterType;

// SVM Estimator
typedef otb::Functor::VariableLengthVectorToMeasurementVectorFunctor<MeasurementType> MeasurementVectorFunctorType;
typedef otb::SVMSampleListModelEstimator<ListSampleType, LabelListSampleType, MeasurementVectorFunctorType>
    SVMEstimatorType;

// ListSample Classifier
typedef otb::SVMClassifier<ListSampleType, LabelType::ValueType> ClassifierType;

// Estimate performance on validation sample
typedef otb::ConfusionMatrixCalculator<LabelListSampleType, LabelListSampleType> ConfusionMatrixCalculatorType;
typedef ConfusionMatrixCalculatorType::ConfusionMatrixType ConfusionMatrixType;
typedef ClassifierType::OutputType ClassifierOutputType;

// Into Image Coordinate system reprojection
typedef otb::VectorDataIntoImageProjectionFilter<VectorDataType, FloatVectorImageType> VectorDataReprojectionType;

// SVM Image Classification
typedef otb::SVMImageClassificationFilter<FloatVectorImageType, Int32ImageType>       ClassificationFilterType;
typedef ClassificationFilterType::Pointer                                             ClassificationFilterPointerType;
typedef otb::ShiftScaleVectorImageFilter<FloatVectorImageType, FloatVectorImageType>  RescalerType;

// From input image to VectorImage
typedef otb::ImageList<FloatImageType>                                        ImageListType;
typedef ImageListToVectorImageFilter<ImageListType,
                                      FloatVectorImageType >                   ListConcatenerFilterType;
typedef MultiToMonoChannelExtractROI<FloatVectorImageType::InternalPixelType,
                                      FloatImageType::PixelType>               ExtractROIFilterType;
typedef ObjectList<ExtractROIFilterType>                                      ExtractROIFilterListType;



typedef otb::StreamingHistogramVectorImageFilter<UInt8VectorImageType> HistogramFilterType;
typedef HistogramFilterType::HistogramType HistogramType;
typedef HistogramFilterType::InternalFilterType::MeasurementVectorType HistoMeasurementVectorType;

class FullSVMClassificationChain: public Application
{
public:
  /** Standard class typedefs. */
  typedef FullSVMClassificationChain Self;
  typedef Application Superclass;
  typedef itk::SmartPointer<Self> Pointer;
  typedef itk::SmartPointer<const Self> ConstPointer;

  /** Standard macro */
  itkNewMacro(Self);

  itkTypeMacro(FullSVMClassificationChain, otb::Application);

private:
  void DoInit()
  {
    SetName("FullSVMClassificationChain");
    //SetDescription("Computes global mean and standard deviation for each band from a set of images and optionally saves the results in an XML file.");
    //SetDocName("Compute Images second order statistics");
    //SetDocLongDescription("This application computes a global mean and standard deviation for each band of a set of images and optionally saves the results in an XML file. The output XML is intended to be used an input for the TrainImagesSVMClassifier application to normalize samples before learning.");
    //SetDocLimitations("Each image of the set must contain the same bands as the others (i.e. same types, in the same order).");
    SetDocAuthors("OTB-Team");
    SetDocSeeAlso("Documentation of the TrainImagesSVMClassifier application.");
 
    AddDocTag(Tags::Learning);
    AddDocTag(Tags::Analysis);
    
    // Group IO
    AddParameter(ParameterType_Group,"io","Input and output data");
    SetParameterDescription("io","This group of parameters allows to set input and output data.");

    AddParameter(ParameterType_InputImageList, "io.il", "Input images");
    SetParameterDescription( "io.il", "List of input images filenames." );

    AddParameter(ParameterType_InputVectorDataList, "io.vd", "Vector Data List");
    SetParameterDescription("io.vd", "A list of vector data to select the training samples.");

    AddParameter(ParameterType_OutputFilename, "io.out",  "Output Image");
    SetParameterDescription( "io.out", "Output image containing class labels");
    
    AddParameter(ParameterType_OutputFilename, "io.results", "Output results");
    SetParameterDescription("io.results", "XML file containing the classification results");
    
    // //Group Sample list
    // AddParameter(ParameterType_Group,"sample","Training and validation samples parameters");
    // SetParameterDescription("sample",
    //                         "This group of parameters allows to set training and validation sample lists parameters.");
 
    // AddParameter(ParameterType_Int, "sample.mt", "Maximum training sample size");
    // SetDefaultParameterInt("sample.mt", -1);
    // SetParameterDescription("sample.mt", "Maximum size of the training sample list (default = -1).");
    // AddParameter(ParameterType_Int, "sample.mv", "Maximum validation sample size");
    // SetDefaultParameterInt("sample.mv", -1);
    // SetParameterDescription("sample.mv", "Maximum size of the validation sample list (default = -1)");

    // AddParameter(ParameterType_Float, "sample.vtr", "training and validation sample ratio");
    // SetParameterDescription("sample.vtr",
    //                         "Ratio between training and validation samples (0.0 = all training, 1.0 = all validation) default = 0.5.");
    // SetParameterFloat("sample.vtr", 0.5);

   // Doc example parameter settings
   // SetDocExampleParameterValue("il", "QB_1_ortho.tif");
   // SetDocExampleParameterValue("out", "EstimateImageStatisticsQB1.xml");
  }

  void DoUpdateParameters()
  {    
    // Nothing to do here : all parameters are independent
  }

  void ConcatenateInputImages()
  {
    otbAppLogINFO("Start concatenation of input images");
    // Initialize the concatenate object in case of application
    // relaunch 
    m_Concatener = ListConcatenerFilterType::New();
    m_ExtractorList = ExtractROIFilterListType::New();
    m_ImageList = ImageListType::New();

    // Get the input image list
    FloatVectorImageListType::Pointer inList = this->GetParameterImageList("io.il");

    if( inList->Size() == 0 )
      {
      itkExceptionMacro("Aucune image disponible...");
      }

    inList->GetNthElement(0)->UpdateOutputInformation();
    FloatVectorImageType::SizeType size = inList->GetNthElement(0)->GetLargestPossibleRegion().GetSize();

    // Split each input vector image into image
    // and generate an mono channel image list
    for( unsigned int i=0; i<inList->Size(); i++ )
      {
      FloatVectorImageType::Pointer vectIm = inList->GetNthElement(i);
      vectIm->UpdateOutputInformation();
      if( size != vectIm->GetLargestPossibleRegion().GetSize() )
        {
        itkExceptionMacro("Input Image size mismatch...");
        }

      for( unsigned int j=0; j<vectIm->GetNumberOfComponentsPerPixel(); j++)
        {
        ExtractROIFilterType::Pointer extractor = ExtractROIFilterType::New();
        extractor->SetInput( vectIm );
        extractor->SetChannel( j+1 );
        extractor->UpdateOutputInformation();
        m_ExtractorList->PushBack( extractor );
        m_ImageList->PushBack( extractor->GetOutput() );
        }
      }
    m_Concatener->SetInput( m_ImageList );
    m_Concatener->UpdateOutputInformation();

    // 
    m_ConcatenatedImage = m_Concatener->GetOutput();

    otbAppLogINFO("End concatenation of input images");
  }
  
  // Added to be sure that the vectorData will contain a ClassKey
  // mandatory to produce SampleListLabels
  void 
  VectorDataSetField(VectorDataType* inputVd, const std::string & fieldName, int fieldValue )
  {
    typedef VectorDataType::DataTreeType            DataTreeType;
    typedef itk::PreOrderTreeIterator<DataTreeType> TreeIteratorType;

    std::ostringstream oss;
    oss << fieldValue;

    TreeIteratorType it(inputVd->GetDataTree());
    for (it.GoToBegin(); !it.IsAtEnd(); ++it)
    {
    it.Get()->SetFieldAsString(fieldName, oss.str());
    }
  }

  void WriteConfusionMatrix(ConfusionMatrixCalculatorType* confusionMatrixCalc, TiXmlElement * results)
  {
    ConfusionMatrixCalculatorType::ConfusionMatrixType matrix = confusionMatrixCalc->GetConfusionMatrix();

    TiXmlElement* matrixxml = new TiXmlElement("MatriceConfusion");
    for (size_t i = 0; i < matrix.Rows(); i++)
    {
      TiXmlElement* rowxml = new TiXmlElement("Class");
      rowxml->SetAttribute("label", i);

      std::ostringstream oss;
      for (size_t j = 0; j < matrix.Cols(); j++)
      {
        oss << matrix[i][j];

        if (j < matrix.Cols() - 1)
          oss << " ";
      }
      TiXmlText * txt = new TiXmlText(oss.str().c_str());
      rowxml->LinkEndChild(txt);
      matrixxml->LinkEndChild(rowxml);
    }
    results->LinkEndChild(matrixxml);

    TiXmlElement* kappaxml = new TiXmlElement("IndiceKappa");
    kappaxml->SetDoubleAttribute("value", confusionMatrixCalc->GetKappaIndex());
    results->LinkEndChild(kappaxml);
    
/*
    oss << confusionMatrixCalc->GetConfusionMatrix() << std::endl;
    {
      
      TiXmlText * txt = new TiXmlText(oss.str().c_str());
      txt->SetCDATA(true);
      xml->LinkEndChild(txt);
      elem->LinkEndChild(xml);
    }



      std::ofstream file;
      file.open(GetParameterString("io.confusion").c_str());

      file << matrix << std::endl;

      file << "Precision of the different class: " << confMatCalc->GetPrecisions() << std::endl;
      file << "Recall of the different class: " << confMatCalc->GetRecalls() << std::endl;
      file << "F-score of the different class: " << confMatCalc->GetFScores() << std::endl;
      file << "Kappa index: " << confMatCalc->GetKappaIndex() << std::endl;

      file.close();
*/
  }

  void WriteStatistics(TiXmlElement * elem)
  {
    typedef otb::ImageFileReader<UInt8VectorImageType> ClassifReaderType;
    ClassifReaderType::Pointer reader = ClassifReaderType::New();
    reader->SetFileName(GetParameterAsString("io.out"));
    reader->UpdateOutputInformation();
    otbAppLogINFO("Reading classification output");

    HistogramFilterType::Pointer histofilter = HistogramFilterType::New();
    histofilter->SetInput(reader->GetOutput());

    size_t nbClass = GetParameterVectorDataList("io.vd")->Size();

    HistoMeasurementVectorType histoMin, histoMax;
    histoMin.SetSize(1);
    histoMin.Fill(0);
    histoMax.SetSize(1);
    histoMax.Fill(nbClass);

    histofilter->GetFilter()->SetHistogramMin(histoMin);
    histofilter->GetFilter()->SetHistogramMax(histoMax);
    histofilter->GetFilter()->SetNumberOfBins(nbClass);
    histofilter->Update();
    otbAppLogINFO("Histogram computed");

    HistogramFilterType::HistogramListType::Pointer histolist = histofilter->GetHistogramList();
    HistogramType::Pointer histo = histolist->GetNthElement(0);

    HistogramType::TotalFrequencyType total = histo->GetTotalFrequency();


    TiXmlElement * stats = new TiXmlElement("Statistiques");
    elem->LinkEndChild(stats);

    // Iterate through the input
    for (unsigned int i = 0; i < nbClass; ++i)
      {
      // get percentage
      double percent = histo->GetFrequency(i, 0) / total * 100;
      // round to nearest 0.1 %
      percent = static_cast<double>(itk::Math::Round( percent * 10 )) / 10;

      // The current statistic
      TiXmlElement * classpercentage = new TiXmlElement("Class");
      classpercentage->SetAttribute("label", i);
      classpercentage->SetDoubleAttribute("pourcentage", percent);
      stats->LinkEndChild( classpercentage );
      }
  }

  void DoExecute()
  {
    // Prepare the XML file
    TiXmlDocument doc;

    TiXmlDeclaration* decl = new TiXmlDeclaration( "1.0", "", "" );
    doc.LinkEndChild( decl );
    TiXmlElement * root = new TiXmlElement( "ClassificationSupervisee");
    doc.LinkEndChild( root );
    TiXmlElement * resultat = new TiXmlElement("Resultats");
    root->LinkEndChild(resultat);


    ConcatenateInputImages();

    //Statistics estimator
    typedef otb::StreamingStatisticsVectorImageFilter<FloatVectorImageType> StreamingStatisticsVImageFilterType;

    // Samples
    typedef double                               ValueType;
    typedef itk::VariableLengthVector<ValueType> MeasurementType;
 
    // Number of bands of the input image
    unsigned int nbBands =  m_ConcatenatedImage->GetNumberOfComponentsPerPixel();
    otbAppLogINFO("Nb bands : "<< nbBands);

    // Get the inputs vectordata
    VectorDataListType* vectorDataList = GetParameterVectorDataList("io.vd");
    
    //Set the measurement vectors size if it's the first iteration
    MeasurementType meanMeasurementVector;
    meanMeasurementVector.SetSize(nbBands);
    meanMeasurementVector.Fill(0.);

    MeasurementType stddevMeasurementVector;
    stddevMeasurementVector.SetSize(nbBands);
    stddevMeasurementVector.Fill(0.);


    // Compute Statistics of each VectorImage
    otbAppLogINFO("Start estimating image statistics");
    unsigned int nbSamples = 0;
    StreamingStatisticsVImageFilterType::Pointer statsEstimator = StreamingStatisticsVImageFilterType::New();
    statsEstimator->SetInput(m_ConcatenatedImage);
    statsEstimator->Update();
    otbAppLogINFO("End estimating image statistics");

    meanMeasurementVector = statsEstimator->GetMean();
    for (unsigned int itBand = 0; itBand < nbBands; itBand++)
      {
      stddevMeasurementVector[itBand] = vcl_sqrt( (statsEstimator->GetCovariance())(itBand, itBand) );
      }

    // ------------------------------------
    // --------- Training ----------------- 
    // ------------------------------------

    //Create training and validation for list samples and label list samples
    ConcatenateLabelListSampleFilterType::Pointer
      concatenateTrainingLabels = ConcatenateLabelListSampleFilterType::New();
    ConcatenateListSampleFilterType::Pointer concatenateTrainingSamples = ConcatenateListSampleFilterType::New();
    ConcatenateLabelListSampleFilterType::Pointer
      concatenateValidationLabels = ConcatenateLabelListSampleFilterType::New();
    ConcatenateListSampleFilterType::Pointer concatenateValidationSamples = ConcatenateListSampleFilterType::New();

    //Iterate over all vectordata
    otbAppLogINFO("Start reprojecting vector data");

    for (unsigned int vdIdx = 0; vdIdx < vectorDataList->Size(); ++vdIdx)
      {
      otbAppLogINFO("Reprojecting vector data #" << vdIdx);

      // Reproject the VectorData in the Image coordinate system
      VectorDataType::Pointer vectorData = vectorDataList->GetNthElement(vdIdx);
      vectorData->Update();
      otbAppLogINFO("Vector data #" << vdIdx << " read successfully");

      vdreproj = VectorDataReprojectionType::New();
      vdreproj->SetInputImage(m_ConcatenatedImage);
      vdreproj->SetInput(vectorData);
      vdreproj->SetUseOutputSpacingAndOriginFromImage(false);
      vdreproj->Update();
      otbAppLogINFO("Vector data #" << vdIdx << " reprojected successfully");

      // Add a field and its value to projected vd
      this->VectorDataSetField(vdreproj->GetOutput(), "Class", vdIdx);
      otbAppLogINFO("Successfully set field value " << vdIdx << " on vector data");

      //Sample list generator
      otbAppLogINFO("Start generating samples for vector data #" << vdIdx);
      ListSampleGeneratorType::Pointer sampleGenerator = ListSampleGeneratorType::New();
      sampleGenerator->SetInput(m_ConcatenatedImage);
      sampleGenerator->SetInputVectorData(vdreproj->GetOutput());
      sampleGenerator->SetClassKey("Class");

      const double validationTrainingProportion = 0.9;
      const size_t trainingSize = 200;
      const size_t validSize = static_cast<long>(trainingSize / (1-validationTrainingProportion));

      sampleGenerator->SetValidationTrainingProportion(validationTrainingProportion);
      sampleGenerator->SetMaxTrainingSize(trainingSize);
      sampleGenerator->SetMaxValidationSize(validSize);
      sampleGenerator->Update();
      otbAppLogINFO("End generating samples for vector data #" << vdIdx);

      //Concatenate training and validation samples from the image
      concatenateTrainingLabels->AddInput(sampleGenerator->GetTrainingListLabel());
      concatenateTrainingSamples->AddInput(sampleGenerator->GetTrainingListSample());
      concatenateValidationLabels->AddInput(sampleGenerator->GetValidationListLabel());
      concatenateValidationSamples->AddInput(sampleGenerator->GetValidationListSample());
      }

    // Update
    otbAppLogINFO("Concatenating sample lists");
    concatenateTrainingSamples->Update();
    concatenateTrainingLabels->Update();
    concatenateValidationSamples->Update();
    concatenateValidationLabels->Update();

    // Do some checking
    if (concatenateTrainingSamples->GetOutputSampleList()->Size() == 0)
      {
      otbAppLogFATAL("No training samples, cannot perform SVM training.");
      }
    if (concatenateValidationSamples->GetOutputSampleList()->Size() == 0)
      {
      otbAppLogWARNING("No validation samples.");
      }

    // Shift scale the samples
    otbAppLogINFO("Starting shift/scale of training samples");
    ShiftScaleFilterType::Pointer trainingShiftScaleFilter = ShiftScaleFilterType::New();
    trainingShiftScaleFilter->SetInput(concatenateTrainingSamples->GetOutput());
    trainingShiftScaleFilter->SetShifts(meanMeasurementVector);
    trainingShiftScaleFilter->SetScales(stddevMeasurementVector);
    trainingShiftScaleFilter->Update();

    otbAppLogINFO("Starting shift/scale of validation samples");
    ShiftScaleFilterType::Pointer validationShiftScaleFilter = ShiftScaleFilterType::New();
    validationShiftScaleFilter->SetInput(concatenateValidationSamples->GetOutput());
    validationShiftScaleFilter->SetShifts(meanMeasurementVector);
    validationShiftScaleFilter->SetScales(stddevMeasurementVector);
    validationShiftScaleFilter->Update();
    otbAppLogINFO("End shift/scale of validation samples");

    // Split the data set into training/validation set
    ListSampleType::Pointer trainingListSample = trainingShiftScaleFilter->GetOutputSampleList();
    ListSampleType::Pointer validationListSample = validationShiftScaleFilter->GetOutputSampleList();
    LabelListSampleType::Pointer trainingLabeledListSample = concatenateTrainingLabels->GetOutputSampleList();
    LabelListSampleType::Pointer validationLabeledListSample = concatenateValidationLabels->GetOutputSampleList();
    otbAppLogINFO("Size of training set: " << trainingListSample->Size());
    otbAppLogINFO("Size of validation set: " << validationListSample->Size());
    otbAppLogINFO("Size of labeled training set: " << trainingLabeledListSample->Size());
    otbAppLogINFO("Size of labeled validation set: " << validationLabeledListSample->Size());

    // Estimate SVM model
    otbAppLogINFO("Starting SVM model estimation");
    SVMEstimatorType::Pointer svmestimator = SVMEstimatorType::New();
    svmestimator->SetInputSampleList(trainingListSample);
    svmestimator->SetTrainingSampleList(trainingLabeledListSample);
    svmestimator->SetParametersOptimization(false);
    svmestimator->Update();

    otbAppLogINFO( "Learning done -> Final SVM accuracy: " 
                   << svmestimator->GetFinalCrossValidationAccuracy() << std::endl);
    otbAppLogINFO( "Number Of Classes : " 
                   << svmestimator->GetModel()->GetNumberOfClasses()  << std::endl);
    otbAppLogINFO( "Number Of Support Vectors : " 
                   << svmestimator->GetModel()->GetNumberOfSupportVectors()  << std::endl);

    // Performances estimation
    otbAppLogINFO("Starting model validation");
    ClassifierType::Pointer validationClassifier = ClassifierType::New();
    validationClassifier->SetSample(validationListSample);
    validationClassifier->SetNumberOfClasses(svmestimator->GetModel()->GetNumberOfClasses());
    validationClassifier->SetModel(svmestimator->GetModel());
    validationClassifier->Update();

    // Estimate performances
    ClassifierOutputType::ConstIterator it = validationClassifier->GetOutput()->Begin();
    ClassifierOutputType::ConstIterator itEnd = validationClassifier->GetOutput()->End();

    LabelListSampleType::Pointer classifierListLabel = LabelListSampleType::New();

    while (it != itEnd)
      {
      // Due to a bug in SVMClassifier, outlier in one-class SVM are labeled with unsigned int max
      classifierListLabel->PushBack(
                                    it.GetClassLabel() 
                                    == itk::NumericTraits<unsigned int>::max() ? 2
                                    : it.GetClassLabel());
      ++it;
      }

    // Compute the confusion matrix
    otbAppLogINFO("Computing confusion matrix");
    ConfusionMatrixCalculatorType::Pointer confMatCalc = ConfusionMatrixCalculatorType::New();
    confMatCalc->SetReferenceLabels(validationLabeledListSample);
    confMatCalc->SetProducedLabels(classifierListLabel);
    confMatCalc->Update();

    // print out the result of the performance estimation
    otbAppLogINFO("SVM training performances :");
    otbAppLogINFO("Confusion matrix:\n" << confMatCalc->GetConfusionMatrix());
    unsigned int nbClass = svmestimator->GetModel()->GetNumberOfClasses();
    for (unsigned int itClasses = 0; itClasses < nbClass; itClasses++)
      {
      otbAppLogINFO("Precision of class [" << itClasses << "] vs all: " << confMatCalc->GetPrecisions()[itClasses]);
      otbAppLogINFO("Recall of class [" << itClasses << "] vs all: " << confMatCalc->GetRecalls()[itClasses]);
      otbAppLogINFO("F-score of class [" << itClasses << "] vs all: " << confMatCalc->GetFScores()[itClasses] << "\n");
      }
    otbAppLogINFO("Global performance, Kappa index: " << confMatCalc->GetKappaIndex());
    
    // Save output in a ascii file (if needed)
    WriteConfusionMatrix(confMatCalc, resultat);

    // ----------------------------------------------
    // ---------- Classification part ---------------
    // ----------------------------------------------
    otbAppLogINFO("Classifying input image");
    m_ClassificationFilter = ClassificationFilterType::New();
    m_ClassificationFilter->SetModel(svmestimator->GetModel());
    
    // Rescale vector image
    m_Rescaler             = RescalerType::New();
    m_Rescaler->SetScale(stddevMeasurementVector);
    m_Rescaler->SetShift(meanMeasurementVector);
    m_Rescaler->SetInput(m_ConcatenatedImage);
    
    m_ClassificationFilter->SetInput(m_Rescaler->GetOutput());

    typedef otb::NeighborhoodMajorityVotingImageFilter<Int32ImageType> NeighborhoodMajorityVotingImageFilterType;
    NeighborhoodMajorityVotingImageFilterType::Pointer majorityvoting = NeighborhoodMajorityVotingImageFilterType::New();
    majorityvoting->SetInput(m_ClassificationFilter->GetOutput());
    majorityvoting->SetLabelForNoDataPixels(255);
    majorityvoting->SetLabelForUndecidedPixels(255);
    majorityvoting->SetKeepOriginalLabelBool(true);

    // Neighborhood majority voting filter settings
    NeighborhoodMajorityVotingImageFilterType::KernelType seBall;
    NeighborhoodMajorityVotingImageFilterType::KernelType::RadiusType rad;
    rad[0] = 1;
    rad[1] = 1;
    seBall.SetRadius(rad);
    seBall.CreateStructuringElement();
    majorityvoting->SetKernel(seBall);

    {
      typedef itk::CastImageFilter<Int32ImageType, UInt8ImageType> CastImageFilterType;
      CastImageFilterType::Pointer cast = CastImageFilterType::New();
      cast->SetInput(majorityvoting->GetOutput());
    
      typedef otb::ImageFileWriter<UInt8ImageType> ClassifWriterType;
      ClassifWriterType::Pointer writer = ClassifWriterType::New();
      writer->SetFileName(GetParameterAsString("io.out"));
      writer->SetInput(cast->GetOutput());
      AddProcess(writer, "Writing classification output");
      writer->Update();
      otbAppLogINFO("Finished writing classification output");
    }

    WriteStatistics(resultat);

    // Finally, write the file
    doc.SaveFile( GetParameterAsString("io.results").c_str() );


  } //end DoExecute

  VectorDataReprojectionType::Pointer vdreproj;
  RescalerType::Pointer               m_Rescaler;
  ClassificationFilterType::Pointer   m_ClassificationFilter;

  FloatVectorImageType::Pointer       m_ConcatenatedImage;

  // Variables for concatenation
  ListConcatenerFilterType::Pointer  m_Concatener;
  ExtractROIFilterListType::Pointer  m_ExtractorList;
  ImageListType::Pointer             m_ImageList;
};

}
}

OTB_APPLICATION_EXPORT(otb::Wrapper::FullSVMClassificationChain)
