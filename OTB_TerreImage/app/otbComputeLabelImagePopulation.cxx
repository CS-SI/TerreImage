
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

// Statistics computation on label image
#include "otbStreamingStatisticsMapFromLabelImageFilter.h"

#include "itkCastImageFilter.h"

#include "itkMath.h"

#include "otb_tinyxml.h"

namespace otb
{
namespace Wrapper
{

  typedef FloatImageType::PixelType PixelType;
  typedef UInt8ImageType LabelImageType;

  typedef otb::StreamingStatisticsMapFromLabelImageFilter<FloatImageType, LabelImageType> StatisticsFilterType;

  // Caster to convert a FloatImageType to LabelImageType
  typedef itk::CastImageFilter
    <FloatImageType, LabelImageType>                   CasterToLabelImageType;

class ComputeLabelImagePopulation: public Application
{
public:
  /** Standard class typedefs. */
  typedef ComputeLabelImagePopulation Self;
  typedef Application Superclass;
  typedef itk::SmartPointer<Self> Pointer;
  typedef itk::SmartPointer<const Self> ConstPointer;

  /** Standard macro */
  itkNewMacro(Self);

  itkTypeMacro(ComputeLabelImagePopulation, otb::Application);

private:
  void DoInit()
  {
    SetName("ComputeLabelImagePopulation");
    SetDescription("TODO");
    SetDocName("TODO");
    SetDocLongDescription("TODO");
    SetDocLimitations("TODO");
    SetDocAuthors("OTB-Team");
    SetDocSeeAlso("TODO");
 
    AddDocTag(Tags::Learning);
    AddDocTag(Tags::Analysis);
    
    // Group IO
    AddParameter(ParameterType_InputImage, "in1", "Input image");
    SetParameterDescription( "in1", "Input image" );
    
    AddParameter(ParameterType_InputImage, "in2", "Input image");
    SetParameterDescription( "in2", "Input image" );

    AddParameter(ParameterType_OutputFilename, "out", "Output results");
    SetParameterDescription("out", "XML file containing the cpopulation results");
    
   // Doc example parameter settings
   // SetDocExampleParameterValue("il", "QB_1_ortho.tif");
   // SetDocExampleParameterValue("out", "EstimateImageStatisticsQB1.xml");
  }

  void DoUpdateParameters()
  {    
    // Nothing to do here : all parameters are independent
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
    
    m_CasterToLabelImage = CasterToLabelImageType::New();
    m_CasterToLabelImage->SetInput(GetParameterFloatImage("in2"));
    m_CasterToLabelImage->InPlaceOn();
    
    m_Statistics = StatisticsFilterType::New();
    m_Statistics->SetInput(GetParameterFloatImage("in1"));
    m_Statistics->SetInputLabelImage(m_CasterToLabelImage->GetOutput());
    m_Statistics->Update();
    
    otbAppLogINFO("Statistics on label image computed");
    
    StatisticsFilterType::LabelPopulationMapType populationMap = m_Statistics->GetLabelPopulationMap();

    TiXmlElement * stats = new TiXmlElement("Statistiques");
    resultat->LinkEndChild(stats);

   
    FloatVectorImageType::SizeType size = GetParameterImage("in1")->GetLargestPossibleRegion().GetSize();
    unsigned int total = size[0] * size[1];
    
    for (StatisticsFilterType::LabelPopulationMapType::const_iterator it = populationMap.begin(); it !=populationMap.end() ; ++it)
    {
      double percent =  (it->second / total) * 100;
      // round to nearest 0.1 %
      percent= static_cast<double>(itk::Math::Round<int, double> ( percent * 10 )) / 10;
    
      // The current statistic
      TiXmlElement * classpercentage = new TiXmlElement("Class");
      classpercentage->SetAttribute("label", it->first);
      classpercentage->SetDoubleAttribute("pourcentage", percent);
      stats->LinkEndChild( classpercentage );
         
    }
   

    // Finally, write the file
    doc.SaveFile( GetParameterAsString("out").c_str() );


  } //end DoExecute
  StatisticsFilterType::Pointer m_Statistics;

  CasterToLabelImageType::Pointer m_CasterToLabelImage;
};

}
}

OTB_APPLICATION_EXPORT(otb::Wrapper::ComputeLabelImagePopulation)
