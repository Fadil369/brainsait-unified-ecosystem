/**
 * BrainSAIT Healthcare OID Tree Data
 * Centralized healthcare-specific OID tree data with Arabic/English support
 */

import type { OidNode } from '../types/oid-tree';

export const createHealthcareOidTreeData = (currentLanguage: string): OidNode => ({
  id: 'root',
  name: currentLanguage === 'ar' ? 'جذر OID' : 'OID Root',
  oid: '1',
  description: currentLanguage === 'ar' 
    ? 'جذر شجرة معرفات الكائنات - نظام BrainSAIT الصحي الموحد'
    : 'Root of the Object Identifier tree - BrainSAIT Unified Healthcare System',
  children: [
    {
      id: 'iso',
      name: currentLanguage === 'ar' ? 'ISO' : 'ISO',
      oid: '1.2',
      description: currentLanguage === 'ar' 
        ? 'المنظمة الدولية للمعايير'
        : 'International Organization for Standardization',
      children: []
    },
    {
      id: 'itu-t',
      name: currentLanguage === 'ar' ? 'ITU-T' : 'ITU-T',
      oid: '1.0',
      description: currentLanguage === 'ar'
        ? 'قطاع توحيد الاتصالات الدولي'
        : 'ITU Telecommunication Standardization Sector',
      children: []
    },
    {
      id: 'joint-iso-itu-t',
      name: currentLanguage === 'ar' ? 'ISO-ITU-T المشترك' : 'Joint ISO-ITU-T',
      oid: '1.1',
      description: currentLanguage === 'ar'
        ? 'الأعمال المشتركة بين ISO و ITU-T'
        : 'Joint work between ISO and ITU-T',
      children: []
    },
    {
      id: 'internet',
      name: currentLanguage === 'ar' ? 'الإنترنت' : 'Internet',
      oid: '1.3',
      description: currentLanguage === 'ar'
        ? 'معرفات الإنترنت والشبكات'
        : 'Internet and networking identifiers',
      children: [
        {
          id: 'dod',
          name: currentLanguage === 'ar' ? 'DoD' : 'DoD',
          oid: '1.3.6',
          description: currentLanguage === 'ar'
            ? 'وزارة الدفاع الأمريكية'
            : 'US Department of Defense',
          children: [
            {
              id: 'internet-directory',
              name: currentLanguage === 'ar' ? 'دليل الإنترنت' : 'Internet Directory',
              oid: '1.3.6.1',
              description: currentLanguage === 'ar'
                ? 'دليل الإنترنت ومعرفات SNMP'
                : 'Internet directory and SNMP identifiers',
              children: [
                {
                  id: 'private',
                  name: currentLanguage === 'ar' ? 'خاص' : 'Private',
                  oid: '1.3.6.1.4',
                  description: currentLanguage === 'ar'
                    ? 'المؤسسات والمنظمات الخاصة'
                    : 'Private enterprises and organizations',
                  children: [
                    {
                      id: 'enterprise',
                      name: currentLanguage === 'ar' ? 'المؤسسات' : 'Enterprise',
                      oid: '1.3.6.1.4.1',
                      description: currentLanguage === 'ar'
                        ? 'أرقام المؤسسات المخصصة من IANA'
                        : 'IANA-assigned enterprise numbers',
                      children: [
                        {
                          id: 'brainsait-ltd',
                          name: currentLanguage === 'ar' ? 'BrainSAIT المحدودة' : 'Brainsait Ltd',
                          oid: '1.3.6.1.4.1.61026',
                          description: currentLanguage === 'ar'
                            ? 'شركة BrainSAIT - منصة الرعاية الصحية الموحدة'
                            : 'Brainsait Ltd - Unified Healthcare Platform Company',
                          organization: 'Brainsait Ltd',
                          country: currentLanguage === 'ar' ? 'السودان' : 'Sudan',
                          registrationAuthority: 'Mohamed Elfadil Abuagla',
                          contact: 'dr.mf.122986@icloud.com',
                          registrationDate: '2023-10-03',
                          healthcareCategory: 'enterprise',
                          children: [
                            {
                              id: 'places',
                              name: currentLanguage === 'ar' ? 'الأماكن' : 'Places',
                              oid: '1.3.6.1.4.1.61026.1',
                              description: currentLanguage === 'ar'
                                ? 'المواقع الجغرافية ومعرفات الأماكن'
                                : 'Geographic locations and place identifiers',
                              healthcareCategory: 'administrative',
                              children: [
                                {
                                  id: 'sudan',
                                  name: currentLanguage === 'ar' ? 'السودان' : 'Sudan',
                                  oid: '1.3.6.1.4.1.61026.1.1',
                                  description: currentLanguage === 'ar'
                                    ? 'جمهورية السودان'
                                    : 'Republic of Sudan',
                                  badgeType: 'geographic',
                                  owner: 'Geographic Registry',
                                  status: 'active',
                                  healthcareCategory: 'administrative',
                                  country: currentLanguage === 'ar' ? 'السودان' : 'Sudan'
                                }
                              ]
                            },
                            {
                              id: 'healthcare-services',
                              name: currentLanguage === 'ar' ? 'خدمات الرعاية الصحية' : 'Healthcare Services',
                              oid: '1.3.6.1.4.1.61026.2',
                              description: currentLanguage === 'ar'
                                ? 'خدمات الرعاية الصحية الأساسية'
                                : 'Core healthcare services',
                              healthcareCategory: 'service',
                              children: [
                                {
                                  id: 'nphies-integration',
                                  name: currentLanguage === 'ar' ? 'تكامل نفيس' : 'NPHIES Integration',
                                  oid: '1.3.6.1.4.1.61026.2.1',
                                  description: currentLanguage === 'ar'
                                    ? 'خدمات تكامل منصة نفيس'
                                    : 'NPHIES platform integration services',
                                  badgeType: 'service',
                                  owner: 'Healthcare IT Department',
                                  status: 'active',
                                  healthcareCategory: 'medical',
                                  nphiesCompliant: true
                                },
                                {
                                  id: 'rcm-system',
                                  name: currentLanguage === 'ar' ? 'نظام إدارة دورة الإيرادات' : 'Revenue Cycle Management',
                                  oid: '1.3.6.1.4.1.61026.2.2',
                                  description: currentLanguage === 'ar'
                                    ? 'نظام إدارة دورة الإيرادات الطبية'
                                    : 'Medical revenue cycle management system',
                                  badgeType: 'service',
                                  owner: 'Finance Department',
                                  status: 'active',
                                  healthcareCategory: 'administrative',
                                  fhirCompliant: true
                                },
                                {
                                  id: 'ai-analytics',
                                  name: currentLanguage === 'ar' ? 'تحليلات الذكاء الاصطناعي' : 'AI Analytics',
                                  oid: '1.3.6.1.4.1.61026.2.3',
                                  description: currentLanguage === 'ar'
                                    ? 'تحليلات الذكاء الاصطناعي للرعاية الصحية'
                                    : 'AI-powered healthcare analytics',
                                  badgeType: 'service',
                                  owner: 'AI Research Team',
                                  status: 'active',
                                  healthcareCategory: 'medical',
                                  aiEnabled: true
                                }
                              ]
                            },
                            {
                              id: 'medical-departments',
                              name: currentLanguage === 'ar' ? 'الأقسام الطبية' : 'Medical Departments',
                              oid: '1.3.6.1.4.1.61026.3',
                              description: currentLanguage === 'ar'
                                ? 'تنظيم الأقسام الطبية'
                                : 'Medical department organization',
                              healthcareCategory: 'department',
                              children: [
                                {
                                  id: 'emergency-dept',
                                  name: currentLanguage === 'ar' ? 'قسم الطوارئ' : 'Emergency Department',
                                  oid: '1.3.6.1.4.1.61026.3.1',
                                  description: currentLanguage === 'ar'
                                    ? 'قسم الطوارئ والعناية الحرجة'
                                    : 'Emergency and critical care department',
                                  badgeType: 'department',
                                  owner: 'Dr. Ahmed Al-Rashid',
                                  status: 'active',
                                  healthcareCategory: 'medical',
                                  priority: 'critical'
                                },
                                {
                                  id: 'cardiology-dept',
                                  name: currentLanguage === 'ar' ? 'قسم القلب' : 'Cardiology Department',
                                  oid: '1.3.6.1.4.1.61026.3.2',
                                  description: currentLanguage === 'ar'
                                    ? 'قسم أمراض القلب والأوعية الدموية'
                                    : 'Cardiovascular diseases department',
                                  badgeType: 'department',
                                  owner: 'Dr. Fatima Al-Zahra',
                                  status: 'active',
                                  healthcareCategory: 'medical',
                                  specialization: 'cardiology'
                                },
                                {
                                  id: 'pediatrics-dept',
                                  name: currentLanguage === 'ar' ? 'قسم الأطفال' : 'Pediatrics Department',
                                  oid: '1.3.6.1.4.1.61026.3.3',
                                  description: currentLanguage === 'ar'
                                    ? 'قسم طب الأطفال وحديثي الولادة'
                                    : 'Pediatrics and neonatal care department',
                                  badgeType: 'department',
                                  owner: 'Dr. Mohammed Al-Saud',
                                  status: 'active',
                                  healthcareCategory: 'medical',
                                  specialization: 'pediatrics'
                                }
                              ]
                            },
                            {
                              id: 'staff-credentials',
                              name: currentLanguage === 'ar' ? 'بيانات اعتماد الموظفين' : 'Staff Credentials',
                              oid: '1.3.6.1.4.1.61026.4',
                              description: currentLanguage === 'ar'
                                ? 'أنظمة بيانات اعتماد الموظفين'
                                : 'Staff credential systems',
                              healthcareCategory: 'administrative',
                              children: [
                                {
                                  id: 'doctor-credentials',
                                  name: currentLanguage === 'ar' ? 'بيانات اعتماد الأطباء' : 'Doctor Credentials',
                                  oid: '1.3.6.1.4.1.61026.4.1',
                                  description: currentLanguage === 'ar'
                                    ? 'نظام بيانات اعتماد الأطباء'
                                    : 'Doctor credential system',
                                  badgeType: 'credential',
                                  owner: 'Medical Board',
                                  status: 'active',
                                  healthcareCategory: 'medical',
                                  roleType: 'doctor'
                                },
                                {
                                  id: 'nurse-credentials',
                                  name: currentLanguage === 'ar' ? 'بيانات اعتماد الممرضين' : 'Nurse Credentials',
                                  oid: '1.3.6.1.4.1.61026.4.2',
                                  description: currentLanguage === 'ar'
                                    ? 'نظام بيانات اعتماد الممرضين'
                                    : 'Nurse credential system',
                                  badgeType: 'credential',
                                  owner: 'Nursing Board',
                                  status: 'active',
                                  healthcareCategory: 'medical',
                                  roleType: 'nurse'
                                },
                                {
                                  id: 'patient-ids',
                                  name: currentLanguage === 'ar' ? 'معرفات المرضى' : 'Patient IDs',
                                  oid: '1.3.6.1.4.1.61026.4.3',
                                  description: currentLanguage === 'ar'
                                    ? 'نظام معرفات المرضى الموحد'
                                    : 'Unified patient identification system',
                                  badgeType: 'identifier',
                                  owner: 'Patient Registration',
                                  status: 'active',
                                  healthcareCategory: 'patient',
                                  roleType: 'patient'
                                }
                              ]
                            },
                            {
                              id: 'training-platform',
                              name: currentLanguage === 'ar' ? 'منصة التدريب' : 'Training Platform',
                              oid: '1.3.6.1.4.1.61026.5',
                              description: currentLanguage === 'ar'
                                ? 'منصة التدريب الطبي والتعليم المستمر'
                                : 'Medical training and continuing education platform',
                              badgeType: 'platform',
                              owner: 'Education Department',
                              status: 'active',
                              healthcareCategory: 'administrative',
                              platform: 'training'
                            },
                            {
                              id: 'bot-operations',
                              name: currentLanguage === 'ar' ? 'عمليات البوت' : 'BOT Operations',
                              oid: '1.3.6.1.4.1.61026.6',
                              description: currentLanguage === 'ar'
                                ? 'عمليات البوت الذكي للمساعدة الطبية'
                                : 'Intelligent BOT operations for medical assistance',
                              badgeType: 'service',
                              owner: 'AI Operations Team',
                              status: 'active',
                              healthcareCategory: 'service',
                              aiEnabled: true,
                              voiceEnabled: true
                            }
                          ]
                        }
                      ]
                    }
                  ]
                },
                {
                  id: 'security',
                  name: currentLanguage === 'ar' ? 'الأمان' : 'Security',
                  oid: '1.3.6.1.5',
                  description: currentLanguage === 'ar'
                    ? 'معرفات الأمان والتشفير'
                    : 'Security and cryptographic identifiers',
                  children: [
                    {
                      id: 'brainsait-security',
                      name: currentLanguage === 'ar' ? 'أمان BrainSAIT' : 'BrainSAIT Security',
                      oid: '1.3.6.1.5.9999',
                      description: currentLanguage === 'ar'
                        ? 'أنظمة الأمان المخصصة لـ BrainSAIT'
                        : 'BrainSAIT dedicated security systems',
                      organization: 'Brainsait Ltd',
                      healthcareCategory: 'security',
                      children: [
                        {
                          id: 'patient-encryption',
                          name: currentLanguage === 'ar' ? 'تشفير بيانات المرضى' : 'Patient Data Encryption',
                          oid: '1.3.6.1.5.9999.1',
                          description: currentLanguage === 'ar'
                            ? 'تشفير بيانات المرضى وفقاً لمعايير HIPAA'
                            : 'Patient data encryption following HIPAA standards',
                          badgeType: 'security',
                          owner: 'Security Team',
                          status: 'active',
                          healthcareCategory: 'security',
                          hipaaCompliant: true
                        }
                      ]
                    }
                  ]
                }
              ]
            }
          ]
        }
      ]
    }
  ]
});

// Generate sample data for performance testing (10,000+ nodes)
export const generateLargeHealthcareDataset = (currentLanguage: string, nodeCount: number = 10000): OidNode => {
  const baseData = createHealthcareOidTreeData(currentLanguage);
  
  // Find the brainsait-ltd node to extend it
  const brainsaitNode = baseData.children?.find(child => 
    child.children?.find(grandchild => 
      grandchild.children?.find(ggchild => 
        ggchild.children?.find(gggchild => 
          gggchild.children?.find(ggggchild => ggggchild.id === 'brainsait-ltd')
        )
      )
    )
  );
  
  if (brainsaitNode) {
    // Add synthetic healthcare data for performance testing
    const syntheticDepartments: OidNode[] = [];
    
    for (let i = 0; i < Math.min(nodeCount, 10000); i++) {
      const deptId = `synthetic-dept-${i}`;
      syntheticDepartments.push({
        id: deptId,
        name: currentLanguage === 'ar' ? `قسم اصطناعي ${i}` : `Synthetic Department ${i}`,
        oid: `1.3.6.1.4.1.61026.1000.${i}`,
        description: currentLanguage === 'ar' 
          ? `قسم اصطناعي لاختبار الأداء رقم ${i}`
          : `Synthetic department for performance testing #${i}`,
        badgeType: 'department',
        owner: `Synthetic Owner ${i}`,
        status: i % 4 === 0 ? 'pending' : 'active',
        healthcareCategory: ['medical', 'administrative', 'patient', 'service'][i % 4] as any,
        nphiesCompliant: i % 3 === 0,
        fhirCompliant: i % 2 === 0,
        hipaaCompliant: i % 5 === 0,
        aiEnabled: i % 7 === 0
      });
    }
    
    // Add synthetic departments to medical-departments
    const findAndAddSynthetic = (node: OidNode): boolean => {
      if (node.id === 'medical-departments') {
        node.children = [...(node.children || []), ...syntheticDepartments];
        return true;
      }
      if (node.children) {
        return node.children.some(child => findAndAddSynthetic(child));
      }
      return false;
    };
    
    findAndAddSynthetic(baseData);
  }
  
  return baseData;
};