import csv
import json
from datetime import datetime
from typing import Dict, List, Optional
import logging
import os

try:
    from reportlab.lib.pagesizes import letter, A4
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib import colors
    from reportlab.lib.units import inch
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False

try:
    import pandas as pd
    PANDAS_AVAILABLE = True
except ImportError:
    PANDAS_AVAILABLE = False

class ResultExporter:
    """
    Professional export module for SEO analysis results
    Supports CSV, JSON, and PDF export formats with customizable templates
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Check and initialize optional dependencies
        self.check_optional_dependencies()
        
        # PDF styles
        if self.reportlab_available:
            self.styles = getSampleStyleSheet()
            self.setup_pdf_styles()
            
    def check_optional_dependencies(self):
        """Check availability of optional dependencies and set flags"""
        # Check ReportLab
        try:
            from reportlab.lib.pagesizes import letter, A4
            from reportlab.platypus import SimpleDocTemplate
            from reportlab.lib.styles import getSampleStyleSheet
            self.reportlab_available = True
        except ImportError:
            self.reportlab_available = False
            self.logger.warning("ReportLab not available. PDF export will be disabled. Install with: pip install reportlab")
            
        # Check Pandas
        try:
            import pandas as pd
            self.pandas_available = True
        except ImportError:
            self.pandas_available = False
            self.logger.warning("Pandas not available. Enhanced Excel export will be disabled. Install with: pip install pandas")
            
        # Check openpyxl for Excel support
        try:
            import openpyxl
            self.excel_available = True
        except ImportError:
            self.excel_available = False
            self.logger.warning("openpyxl not available. Excel export will be disabled. Install with: pip install openpyxl")
        
    def setup_pdf_styles(self):
        """Setup custom PDF styles for professional reports"""
        if not REPORTLAB_AVAILABLE:
            return
            
        # Custom title style
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Title'],
            fontSize=24,
            spaceAfter=30,
            textColor=colors.darkblue,
            alignment=1  # Center alignment
        ))
        
        # Custom heading style
        self.styles.add(ParagraphStyle(
            name='CustomHeading',
            parent=self.styles['Heading1'],
            fontSize=16,
            spaceAfter=12,
            spaceBefore=20,
            textColor=colors.darkblue,
            borderWidth=1,
            borderColor=colors.darkblue,
            borderPadding=5
        ))
        
        # Custom subtitle style
        self.styles.add(ParagraphStyle(
            name='CustomSubtitle',
            parent=self.styles['Normal'],
            fontSize=12,
            spaceAfter=20,
            textColor=colors.grey,
            alignment=1
        ))
        
    def export_to_csv(self, filename: str, competitor_keywords: Dict[str, Dict],
                     missing_keywords: List[Dict], metadata: Dict) -> bool:
        """
        Export analysis results to CSV format
        
        Args:
            filename: Output filename
            competitor_keywords: Competitor keyword data
            missing_keywords: Missing keyword opportunities
            metadata: Analysis metadata
            
        Returns:
            True if export successful, False otherwise
        """
        try:
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(filename), exist_ok=True)
            
            if PANDAS_AVAILABLE:
                return self._export_csv_pandas(filename, competitor_keywords, missing_keywords, metadata)
            else:
                return self._export_csv_standard(filename, competitor_keywords, missing_keywords, metadata)
                
        except Exception as e:
            self.logger.error(f"Error exporting to CSV: {str(e)}")
            return False
            
    def _export_csv_pandas(self, filename: str, competitor_keywords: Dict[str, Dict],
                          missing_keywords: List[Dict], metadata: Dict) -> bool:
        """Export using pandas for enhanced functionality"""
        with pd.ExcelWriter(filename.replace('.csv', '.xlsx'), engine='openpyxl') as writer:
            # Metadata sheet
            metadata_df = pd.DataFrame([metadata])
            metadata_df.to_excel(writer, sheet_name='Analysis_Info', index=False)
            
            # Competitor keywords sheet
            if competitor_keywords:
                comp_data = []
                for keyword, data in competitor_keywords.items():
                    comp_data.append({
                        'Keyword': keyword,
                        'Frequency': data.get('frequency', 0),
                        'Document_Frequency': data.get('document_frequency', 0),
                        'Avg_Importance': round(data.get('avg_importance', 0), 2),
                        'Sources': len(data.get('sources', [])),
                        'Avg_Position': round(data.get('avg_position', 0), 2)
                    })
                
                comp_df = pd.DataFrame(comp_data)
                comp_df.to_excel(writer, sheet_name='Competitor_Keywords', index=False)
            
            # Missing keywords sheet
            if missing_keywords:
                missing_df = pd.DataFrame(missing_keywords)
                # Select relevant columns for export
                export_columns = [
                    'keyword', 'opportunity_score', 'priority', 'competitor_frequency',
                    'found_in_sites', 'keyword_type', 'search_intent', 'estimated_difficulty'
                ]
                missing_df = missing_df[export_columns]
                missing_df.to_excel(writer, sheet_name='Missing_Keywords', index=False)
                
        # Also create CSV version
        self._create_summary_csv(filename, competitor_keywords, missing_keywords, metadata)
        return True
        
    def _export_csv_standard(self, filename: str, competitor_keywords: Dict[str, Dict],
                           missing_keywords: List[Dict], metadata: Dict) -> bool:
        """Export using standard CSV library"""
        # Create main summary CSV
        self._create_summary_csv(filename, competitor_keywords, missing_keywords, metadata)
        
        # Create separate detailed files
        base_filename = filename.replace('.csv', '')
        
        # Competitor keywords CSV
        comp_filename = f"{base_filename}_competitor_keywords.csv"
        self._create_competitor_csv(comp_filename, competitor_keywords)
        
        # Missing keywords CSV
        missing_filename = f"{base_filename}_missing_keywords.csv"
        self._create_missing_csv(missing_filename, missing_keywords)
        
        return True
        
    def _create_summary_csv(self, filename: str, competitor_keywords: Dict[str, Dict],
                           missing_keywords: List[Dict], metadata: Dict):
        """Create summary CSV file"""
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            
            # Write metadata
            writer.writerow(['SEO Content Gap Analysis Report'])
            writer.writerow(['Generated:', datetime.now().strftime('%Y-%m-%d %H:%M:%S')])
            writer.writerow(['Target Keyword:', metadata.get('keyword', '')])
            writer.writerow(['Location:', metadata.get('location', 'Not specified')])
            writer.writerow([])
            
            # Summary statistics
            writer.writerow(['ANALYSIS SUMMARY'])
            writer.writerow(['Competitor Keywords Found:', len(competitor_keywords)])
            writer.writerow(['Missing Keywords Identified:', len(missing_keywords)])
            
            if missing_keywords:
                high_priority = len([k for k in missing_keywords if k['priority'] == 'high'])
                medium_priority = len([k for k in missing_keywords if k['priority'] == 'medium'])
                low_priority = len([k for k in missing_keywords if k['priority'] == 'low'])
                
                writer.writerow(['High Priority Opportunities:', high_priority])
                writer.writerow(['Medium Priority Opportunities:', medium_priority])
                writer.writerow(['Low Priority Opportunities:', low_priority])
            
            writer.writerow([])
            
            # Top missing keywords
            writer.writerow(['TOP MISSING KEYWORDS'])
            writer.writerow(['Keyword', 'Opportunity Score', 'Priority', 'Competitor Frequency', 'Type'])
            
            for keyword_data in sorted(missing_keywords, key=lambda x: x['opportunity_score'], reverse=True)[:20]:
                writer.writerow([
                    keyword_data['keyword'],
                    round(keyword_data['opportunity_score'], 1),
                    keyword_data['priority'],
                    keyword_data['competitor_frequency'],
                    keyword_data['keyword_type']
                ])
                
    def _create_competitor_csv(self, filename: str, competitor_keywords: Dict[str, Dict]):
        """Create detailed competitor keywords CSV"""
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            
            # Header
            writer.writerow([
                'Keyword', 'Frequency', 'Document_Frequency', 'Avg_Importance',
                'Sources', 'Avg_Position'
            ])
            
            # Data rows
            for keyword, data in sorted(competitor_keywords.items(), 
                                      key=lambda x: x[1].get('frequency', 0), reverse=True):
                writer.writerow([
                    keyword,
                    data.get('frequency', 0),
                    data.get('document_frequency', 0),
                    round(data.get('avg_importance', 0), 2),
                    len(data.get('sources', [])),
                    round(data.get('avg_position', 0), 2)
                ])
                
    def _create_missing_csv(self, filename: str, missing_keywords: List[Dict]):
        """Create detailed missing keywords CSV"""
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            
            # Header
            writer.writerow([
                'Keyword', 'Opportunity_Score', 'Priority', 'Competitor_Frequency',
                'Found_In_Sites', 'Keyword_Type', 'Search_Intent', 'Estimated_Difficulty',
                'Word_Count', 'Recommendations'
            ])
            
            # Data rows
            for keyword_data in sorted(missing_keywords, key=lambda x: x['opportunity_score'], reverse=True):
                recommendations = '; '.join(keyword_data.get('recommendations', []))
                writer.writerow([
                    keyword_data['keyword'],
                    round(keyword_data['opportunity_score'], 1),
                    keyword_data['priority'],
                    keyword_data['competitor_frequency'],
                    keyword_data['found_in_sites'],
                    keyword_data['keyword_type'],
                    keyword_data['search_intent'],
                    keyword_data['estimated_difficulty'],
                    keyword_data['word_count'],
                    recommendations
                ])
                
    def export_to_pdf(self, filename: str, competitor_keywords: Dict[str, Dict],
                     missing_keywords: List[Dict], metadata: Dict) -> bool:
        """
        Export analysis results to professional PDF report
        
        Args:
            filename: Output filename
            competitor_keywords: Competitor keyword data
            missing_keywords: Missing keyword opportunities
            metadata: Analysis metadata
            
        Returns:
            True if export successful, False otherwise
        """
        if not REPORTLAB_AVAILABLE:
            self.logger.error("ReportLab not available. Install with: pip install reportlab")
            return False
            
        try:
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(filename), exist_ok=True)
            
            # Create PDF document
            doc = SimpleDocTemplate(filename, pagesize=A4, topMargin=0.75*inch, bottomMargin=0.75*inch)
            story = []
            
            # Title page
            self._add_title_page(story, metadata)
            
            # Executive summary
            self._add_executive_summary(story, competitor_keywords, missing_keywords)
            
            # Competitor analysis
            self._add_competitor_analysis(story, competitor_keywords)
            
            # Missing keywords analysis
            self._add_missing_keywords_analysis(story, missing_keywords)
            
            # Recommendations
            self._add_recommendations(story, missing_keywords)
            
            # Build PDF
            doc.build(story)
            return True
            
        except Exception as e:
            self.logger.error(f"Error exporting to PDF: {str(e)}")
            return False
            
    def _add_title_page(self, story: List, metadata: Dict):
        """Add title page to PDF"""
        # Title
        title = Paragraph("SEO Content Gap Analysis Report", self.styles['CustomTitle'])
        story.append(title)
        story.append(Spacer(1, 0.5*inch))
        
        # Subtitle with analysis details
        subtitle_text = f"""
        Target Keyword: {metadata.get('keyword', 'Not specified')}<br/>
        Location: {metadata.get('location', 'Not specified')}<br/>
        Analysis Date: {datetime.now().strftime('%B %d, %Y')}<br/>
        Generated at: {datetime.now().strftime('%I:%M %p')}
        """
        subtitle = Paragraph(subtitle_text, self.styles['CustomSubtitle'])
        story.append(subtitle)
        story.append(PageBreak())
        
    def _add_executive_summary(self, story: List, competitor_keywords: Dict[str, Dict],
                              missing_keywords: List[Dict]):
        """Add executive summary section"""
        # Section header
        header = Paragraph("Executive Summary", self.styles['CustomHeading'])
        story.append(header)
        
        # Summary statistics
        total_competitor_keywords = len(competitor_keywords)
        total_missing_keywords = len(missing_keywords)
        
        if missing_keywords:
            high_priority = len([k for k in missing_keywords if k['priority'] == 'high'])
            medium_priority = len([k for k in missing_keywords if k['priority'] == 'medium'])
            low_priority = len([k for k in missing_keywords if k['priority'] == 'low'])
        else:
            high_priority = medium_priority = low_priority = 0
            
        summary_text = f"""
        This analysis identified significant opportunities for content optimization and keyword targeting.
        
        <b>Key Findings:</b><br/>
        • Analyzed {total_competitor_keywords} competitor keywords<br/>
        • Identified {total_missing_keywords} missing keyword opportunities<br/>
        • Found {high_priority} high-priority optimization targets<br/>
        • Discovered {medium_priority} medium-priority opportunities<br/>
        • Located {low_priority} additional long-term targets<br/>
        
        <b>Strategic Recommendations:</b><br/>
        Focus immediate efforts on high-priority keywords that offer the greatest opportunity for 
        improved search visibility and competitive advantage. These keywords demonstrate strong 
        competitor usage while being absent from current content strategy.
        """
        
        summary = Paragraph(summary_text, self.styles['Normal'])
        story.append(summary)
        story.append(Spacer(1, 0.3*inch))
        
    def _add_competitor_analysis(self, story: List, competitor_keywords: Dict[str, Dict]):
        """Add competitor keyword analysis section"""
        if not competitor_keywords:
            return
            
        header = Paragraph("Competitor Keyword Analysis", self.styles['CustomHeading'])
        story.append(header)
        
        # Introduction
        intro_text = f"""
        Analysis of competitor content revealed {len(competitor_keywords)} unique keywords 
        across the top-ranking websites. The following table presents the most frequently 
        used keywords that contribute to competitor search visibility.
        """
        intro = Paragraph(intro_text, self.styles['Normal'])
        story.append(intro)
        story.append(Spacer(1, 0.2*inch))
        
        # Prepare table data
        table_data = [['Keyword', 'Frequency', 'Sites Using', 'Avg Importance']]
        
        # Sort by frequency and take top 25
        sorted_keywords = sorted(competitor_keywords.items(), 
                               key=lambda x: x[1].get('frequency', 0), reverse=True)[:25]
        
        for keyword, data in sorted_keywords:
            table_data.append([
                keyword,
                str(data.get('frequency', 0)),
                str(len(data.get('sources', []))),
                f"{data.get('avg_importance', 0):.1f}"
            ])
            
        # Create and style table
        table = Table(table_data, colWidths=[3*inch, 1*inch, 1*inch, 1.2*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.darkblue),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        story.append(table)
        story.append(PageBreak())
        
    def _add_missing_keywords_analysis(self, story: List, missing_keywords: List[Dict]):
        """Add missing keywords analysis section"""
        if not missing_keywords:
            return
            
        header = Paragraph("Missing Keywords & Opportunities", self.styles['CustomHeading'])
        story.append(header)
        
        # Introduction
        intro_text = f"""
        The following analysis identifies {len(missing_keywords)} keyword opportunities 
        that are currently underutilized in your content strategy but demonstrate strong 
        competitor usage and search potential.
        """
        intro = Paragraph(intro_text, self.styles['Normal'])
        story.append(intro)
        story.append(Spacer(1, 0.2*inch))
        
        # High priority opportunities table
        high_priority_keywords = [k for k in missing_keywords if k['priority'] == 'high'][:15]
        
        if high_priority_keywords:
            subheader = Paragraph("High Priority Opportunities", self.styles['Heading2'])
            story.append(subheader)
            
            table_data = [['Keyword', 'Score', 'Type', 'Intent', 'Competitor Freq']]
            
            for kw in high_priority_keywords:
                table_data.append([
                    kw['keyword'],
                    f"{kw['opportunity_score']:.1f}",
                    kw['keyword_type'],
                    kw['search_intent'],
                    str(kw['competitor_frequency'])
                ])
                
            table = Table(table_data, colWidths=[2.5*inch, 0.8*inch, 1*inch, 1*inch, 1*inch])
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.darkred),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('BACKGROUND', (0, 1), (-1, -1), colors.lightgrey),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            
            story.append(table)
            story.append(Spacer(1, 0.3*inch))
            
    def _add_recommendations(self, story: List, missing_keywords: List[Dict]):
        """Add strategic recommendations section"""
        header = Paragraph("Strategic Recommendations", self.styles['CustomHeading'])
        story.append(header)
        
        if not missing_keywords:
            no_opportunities = Paragraph("No significant keyword opportunities identified at this time.", 
                                       self.styles['Normal'])
            story.append(no_opportunities)
            return
            
        # Generate recommendations based on analysis
        high_priority = [k for k in missing_keywords if k['priority'] == 'high']
        medium_priority = [k for k in missing_keywords if k['priority'] == 'medium']
        
        recommendations_text = "<b>Immediate Actions (Next 30 Days):</b><br/>"
        
        if high_priority:
            recommendations_text += f"• Target the {len(high_priority)} high-priority keywords identified in this analysis<br/>"
            recommendations_text += f"• Create dedicated content for top opportunities: {', '.join([k['keyword'] for k in high_priority[:3]])}<br/>"
            
        if medium_priority:
            recommendations_text += f"• Plan content calendar addressing {len(medium_priority)} medium-priority opportunities<br/>"
            
        recommendations_text += "<br/><b>Long-term Strategy (Next 90 Days):</b><br/>"
        recommendations_text += "• Develop comprehensive content strategy targeting identified keyword gaps<br/>"
        recommendations_text += "• Monitor competitor content for new keyword opportunities<br/>"
        recommendations_text += "• Implement regular content gap analysis to maintain competitive advantage<br/>"
        recommendations_text += "• Track keyword ranking improvements and adjust strategy accordingly"
        
        recommendations = Paragraph(recommendations_text, self.styles['Normal'])
        story.append(recommendations)
        
    def export_to_json(self, filename: str, competitor_keywords: Dict[str, Dict],
                      missing_keywords: List[Dict], metadata: Dict) -> bool:
        """
        Export analysis results to JSON format
        
        Args:
            filename: Output filename
            competitor_keywords: Competitor keyword data
            missing_keywords: Missing keyword opportunities
            metadata: Analysis metadata
            
        Returns:
            True if export successful, False otherwise
        """
        try:
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(filename), exist_ok=True)
            
            export_data = {
                'metadata': {
                    **metadata,
                    'export_timestamp': datetime.now().isoformat(),
                    'total_competitor_keywords': len(competitor_keywords),
                    'total_missing_keywords': len(missing_keywords)
                },
                'competitor_keywords': competitor_keywords,
                'missing_keywords': missing_keywords,
                'summary_statistics': self._generate_summary_stats(competitor_keywords, missing_keywords)
            }
            
            with open(filename, 'w', encoding='utf-8') as jsonfile:
                json.dump(export_data, jsonfile, indent=2, ensure_ascii=False)
                
            return True
            
        except Exception as e:
            self.logger.error(f"Error exporting to JSON: {str(e)}")
            return False
            
    def _generate_summary_stats(self, competitor_keywords: Dict[str, Dict],
                               missing_keywords: List[Dict]) -> Dict:
        """Generate summary statistics for export"""
        stats = {
            'competitor_analysis': {
                'total_keywords': len(competitor_keywords),
                'avg_frequency': 0,
                'top_keywords': []
            },
            'opportunity_analysis': {
                'total_opportunities': len(missing_keywords),
                'high_priority': 0,
                'medium_priority': 0,
                'low_priority': 0,
                'avg_opportunity_score': 0
            }
        }
        
        # Competitor stats
        if competitor_keywords:
            frequencies = [data.get('frequency', 0) for data in competitor_keywords.values()]
            stats['competitor_analysis']['avg_frequency'] = sum(frequencies) / len(frequencies)
            
            top_keywords = sorted(competitor_keywords.items(), 
                                key=lambda x: x[1].get('frequency', 0), reverse=True)[:10]
            stats['competitor_analysis']['top_keywords'] = [kw[0] for kw in top_keywords]
            
        # Opportunity stats
        if missing_keywords:
            for opportunity in missing_keywords:
                priority = opportunity['priority']
                stats['opportunity_analysis'][f'{priority}_priority'] += 1
                
            scores = [kw['opportunity_score'] for kw in missing_keywords]
            stats['opportunity_analysis']['avg_opportunity_score'] = sum(scores) / len(scores)
            
        return stats
        
    def create_batch_export(self, base_filename: str, competitor_keywords: Dict[str, Dict],
                           missing_keywords: List[Dict], metadata: Dict,
                           formats: List[str] = ['csv', 'json', 'pdf']) -> Dict[str, bool]:
        """
        Export results in multiple formats simultaneously
        
        Args:
            base_filename: Base filename without extension
            competitor_keywords: Competitor keyword data
            missing_keywords: Missing keyword opportunities
            metadata: Analysis metadata
            formats: List of formats to export ('csv', 'json', 'pdf')
            
        Returns:
            Dictionary mapping format to success status
        """
        results = {}
        
        for format_type in formats:
            filename = f"{base_filename}.{format_type}"
            
            if format_type == 'csv':
                results['csv'] = self.export_to_csv(filename, competitor_keywords, missing_keywords, metadata)
            elif format_type == 'json':
                results['json'] = self.export_to_json(filename, competitor_keywords, missing_keywords, metadata)
            elif format_type == 'pdf':
                results['pdf'] = self.export_to_pdf(filename, competitor_keywords, missing_keywords, metadata)
            else:
                self.logger.warning(f"Unsupported export format: {format_type}")
                results[format_type] = False
                
        return results