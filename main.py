import tkinter as tk
from tkinter import ttk, scrolledtext, filedialog, messagebox
import threading
import json
import os
from datetime import datetime
import webbrowser
import requests

from scraper import GoogleScraper
from analyzer import KeywordAnalyzer
from gap_finder import ContentGapFinder
from exporter import ResultExporter
import config
from logging_config import setup_logging, PerformanceTimer

# Initialize logging
setup_logging()

class SEOAnalyzerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Local SEO Rank & Content Gap Analyzer Pro")
        self.root.geometry("1400x900")
        self.root.minsize(1200, 800)
        
        # Initialize components
        self.scraper = GoogleScraper()
        self.analyzer = KeywordAnalyzer()
        self.gap_finder = ContentGapFinder()
        self.exporter = ResultExporter()
        
        # Data storage
        self.current_results = {}
        self.competitor_keywords = {}
        self.user_content_keywords = {}
        self.missing_keywords = []
        
        # Setup GUI
        self.setup_styles()
        self.create_menu()
        self.create_main_interface()
        self.create_status_bar()
        
        # Load previous session if exists
        self.load_session()
        
    def setup_styles(self):
        """Configure custom styles for the application"""
        style = ttk.Style()
        style.theme_use('clam')
        
        # Custom button styles
        style.configure('Action.TButton', 
                       background='#4CAF50', 
                       foreground='white',
                       padding=(10, 5))
        
        style.configure('Export.TButton',
                       background='#2196F3',
                       foreground='white',
                       padding=(8, 4))
        
        # Custom frame styles
        style.configure('Card.TFrame',
                       background='#f8f9fa',
                       relief='ridge',
                       borderwidth=1)
        
    def create_menu(self):
        """Create application menu bar"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="New Analysis", command=self.new_analysis)
        file_menu.add_command(label="Save Results", command=self.save_results)
        file_menu.add_command(label="Load Results", command=self.load_results)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)
        
        # Tools menu
        tools_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Tools", menu=tools_menu)
        tools_menu.add_command(label="Settings", command=self.open_settings)
        tools_menu.add_command(label="Keyword History", command=self.show_history)
        tools_menu.add_command(label="Batch Analysis", command=self.batch_analysis)
        
        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="User Guide", command=self.show_help)
        help_menu.add_command(label="API Documentation", command=self.show_api_docs)
        help_menu.add_command(label="About", command=self.show_about)
        
    def create_main_interface(self):
        """Create the main interface layout"""
        # Main container with padding
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(2, weight=1)
        
        # Input section
        self.create_input_section(main_frame)
        
        # Control buttons section
        self.create_control_section(main_frame)
        
        # Results section
        self.create_results_section(main_frame)
        
        # Export section
        self.create_export_section(main_frame)
        
    def create_input_section(self, parent):
        """Create input fields section"""
        input_frame = ttk.LabelFrame(parent, text="Analysis Configuration", padding="10")
        input_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        input_frame.columnconfigure(1, weight=1)
        
        # Target keyword input
        ttk.Label(input_frame, text="Target Keyword:").grid(row=0, column=0, sticky=tk.W, padx=(0, 10))
        self.keyword_var = tk.StringVar()
        keyword_entry = ttk.Entry(input_frame, textvariable=self.keyword_var, width=50, font=('Arial', 10))
        keyword_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(0, 10))
        
        # Location input
        ttk.Label(input_frame, text="Location (Optional):").grid(row=0, column=2, sticky=tk.W, padx=(10, 10))
        self.location_var = tk.StringVar()
        location_entry = ttk.Entry(input_frame, textvariable=self.location_var, width=30, font=('Arial', 10))
        location_entry.grid(row=0, column=3, sticky=(tk.W, tk.E))
        
        # Number of results
        ttk.Label(input_frame, text="Results Count:").grid(row=1, column=0, sticky=tk.W, padx=(0, 10), pady=(10, 0))
        self.results_count_var = tk.IntVar(value=10)
        results_spin = ttk.Spinbox(input_frame, from_=5, to=20, textvariable=self.results_count_var, width=10)
        results_spin.grid(row=1, column=1, sticky=tk.W, pady=(10, 0))
        
        # User content input method selection
        ttk.Label(input_frame, text="Content Source:").grid(row=1, column=2, sticky=tk.W, padx=(10, 10), pady=(10, 0))
        self.content_method_var = tk.StringVar(value="url")
        method_frame = ttk.Frame(input_frame)
        method_frame.grid(row=1, column=3, sticky=(tk.W, tk.E), pady=(10, 0))
        
        ttk.Radiobutton(method_frame, text="URL", variable=self.content_method_var, 
                       value="url", command=self.toggle_content_input).pack(side=tk.LEFT)
        ttk.Radiobutton(method_frame, text="Text", variable=self.content_method_var, 
                       value="text", command=self.toggle_content_input).pack(side=tk.LEFT, padx=(10, 0))
        ttk.Radiobutton(method_frame, text="File", variable=self.content_method_var, 
                       value="file", command=self.toggle_content_input).pack(side=tk.LEFT, padx=(10, 0))
        
        # User content/URL input
        content_frame = ttk.Frame(input_frame)
        content_frame.grid(row=2, column=0, columnspan=4, sticky=(tk.W, tk.E), pady=(10, 0))
        content_frame.columnconfigure(0, weight=1)
        
        self.content_label = ttk.Label(content_frame, text="Your Website URL:")
        self.content_label.grid(row=0, column=0, sticky=tk.W, pady=(0, 5))
        
        self.content_input_frame = ttk.Frame(content_frame)
        self.content_input_frame.grid(row=1, column=0, sticky=(tk.W, tk.E))
        self.content_input_frame.columnconfigure(0, weight=1)
        
        self.content_var = tk.StringVar()
        self.content_entry = ttk.Entry(self.content_input_frame, textvariable=self.content_var, 
                                      font=('Arial', 10))
        self.content_entry.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 10))
        
        self.browse_button = ttk.Button(self.content_input_frame, text="Browse", 
                                       command=self.browse_file, state=tk.DISABLED)
        self.browse_button.grid(row=0, column=1)
        
        # Advanced options collapsible section
        self.create_advanced_options(input_frame)
        
    def create_advanced_options(self, parent):
        """Create collapsible advanced options section"""
        self.advanced_visible = tk.BooleanVar(value=False)
        
        advanced_toggle = ttk.Checkbutton(parent, text="Show Advanced Options", 
                                         variable=self.advanced_visible,
                                         command=self.toggle_advanced_options)
        advanced_toggle.grid(row=3, column=0, columnspan=4, sticky=tk.W, pady=(15, 5))
        
        self.advanced_frame = ttk.Frame(parent)
        self.advanced_frame.grid(row=4, column=0, columnspan=4, sticky=(tk.W, tk.E), pady=(5, 0))
        self.advanced_frame.columnconfigure(1, weight=1)
        
        # Minimum keyword frequency
        ttk.Label(self.advanced_frame, text="Min Keyword Frequency:").grid(row=0, column=0, sticky=tk.W, padx=(0, 10))
        self.min_frequency_var = tk.IntVar(value=2)
        ttk.Spinbox(self.advanced_frame, from_=1, to=10, textvariable=self.min_frequency_var, width=10).grid(row=0, column=1, sticky=tk.W)
        
        # Exclude common words
        self.exclude_common_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(self.advanced_frame, text="Exclude Common Words", 
                       variable=self.exclude_common_var).grid(row=0, column=2, sticky=tk.W, padx=(20, 0))
        
        # Custom stopwords
        ttk.Label(self.advanced_frame, text="Custom Stopwords:").grid(row=1, column=0, sticky=tk.W, padx=(0, 10), pady=(10, 0))
        self.custom_stopwords_var = tk.StringVar()
        stopwords_entry = ttk.Entry(self.advanced_frame, textvariable=self.custom_stopwords_var, width=50)
        stopwords_entry.grid(row=1, column=1, columnspan=2, sticky=(tk.W, tk.E), pady=(10, 0))
        
        # Initially hide advanced options
        self.advanced_frame.grid_remove()
        
    def toggle_advanced_options(self):
        """Toggle visibility of advanced options"""
        if self.advanced_visible.get():
            self.advanced_frame.grid()
        else:
            self.advanced_frame.grid_remove()
            
    def toggle_content_input(self):
        """Toggle between URL, text, and file input methods"""
        method = self.content_method_var.get()
        
        if method == "url":
            self.content_label.config(text="Your Website URL:")
            self.content_entry.grid()
            self.browse_button.config(state=tk.DISABLED)
            
        elif method == "text":
            self.content_label.config(text="Your Content Text:")
            self.content_entry.grid()
            self.browse_button.config(state=tk.DISABLED)
            
        elif method == "file":
            self.content_label.config(text="Content File:")
            self.content_entry.grid()
            self.browse_button.config(state=tk.NORMAL)
            
    def browse_file(self):
        """Open file browser for content file selection"""
        filename = filedialog.askopenfilename(
            title="Select Content File",
            filetypes=[("Text files", "*.txt"), ("HTML files", "*.html"), ("All files", "*.*")]
        )
        if filename:
            self.content_var.set(filename)
            
    def create_control_section(self, parent):
        """Create control buttons section"""
        control_frame = ttk.Frame(parent)
        control_frame.grid(row=1, column=0, columnspan=2, pady=(0, 10))
        
        # Main analyze button
        self.analyze_button = ttk.Button(control_frame, text="🔍 Start Analysis", 
                                        command=self.start_analysis, 
                                        style='Action.TButton')
        self.analyze_button.pack(side=tk.LEFT, padx=(0, 10))
        
        # Stop button
        self.stop_button = ttk.Button(control_frame, text="⏹ Stop", 
                                     command=self.stop_analysis, 
                                     state=tk.DISABLED)
        self.stop_button.pack(side=tk.LEFT, padx=(0, 10))
        
        # Clear results button
        ttk.Button(control_frame, text="🗑 Clear Results", 
                  command=self.clear_results).pack(side=tk.LEFT, padx=(0, 10))
        
        # Progress bar
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(control_frame, variable=self.progress_var, 
                                          length=200, mode='determinate')
        self.progress_bar.pack(side=tk.LEFT, padx=(20, 10))
        
        # Progress label
        self.progress_label = ttk.Label(control_frame, text="Ready")
        self.progress_label.pack(side=tk.LEFT)
        
    def create_results_section(self, parent):
        """Create results display section"""
        results_frame = ttk.LabelFrame(parent, text="Analysis Results", padding="10")
        results_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        results_frame.columnconfigure(0, weight=1)
        results_frame.columnconfigure(1, weight=1)
        results_frame.rowconfigure(1, weight=1)
        
        # Results tabs
        self.notebook = ttk.Notebook(results_frame)
        self.notebook.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        
        # Competitor keywords tab
        self.competitor_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.competitor_frame, text="Competitor Keywords")
        
        # Create competitor keywords interface
        self.create_competitor_keywords_tab()
        
        # Missing keywords tab
        self.missing_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.missing_frame, text="Missing Keywords")
        
        # Create missing keywords interface
        self.create_missing_keywords_tab()
        
        # Analysis summary tab
        self.summary_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.summary_frame, text="Analysis Summary")
        
        # Create summary interface
        self.create_summary_tab()
        
        # Detailed report tab
        self.report_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.report_frame, text="Detailed Report")
        
        # Create detailed report interface
        self.create_report_tab()
        
    def create_competitor_keywords_tab(self):
        """Create competitor keywords analysis tab"""
        self.competitor_frame.columnconfigure(0, weight=1)
        self.competitor_frame.rowconfigure(1, weight=1)
        
        # Filter controls
        filter_frame = ttk.Frame(self.competitor_frame)
        filter_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        
        ttk.Label(filter_frame, text="Filter by frequency:").pack(side=tk.LEFT)
        self.freq_filter_var = tk.IntVar(value=1)
        ttk.Spinbox(filter_frame, from_=1, to=10, textvariable=self.freq_filter_var, 
                   width=10, command=self.filter_competitor_keywords).pack(side=tk.LEFT, padx=(5, 15))
        
        ttk.Label(filter_frame, text="Search:").pack(side=tk.LEFT)
        self.keyword_search_var = tk.StringVar()
        search_entry = ttk.Entry(filter_frame, textvariable=self.keyword_search_var, width=20)
        search_entry.pack(side=tk.LEFT, padx=(5, 10))
        search_entry.bind('<KeyRelease>', self.search_keywords)
        
        # Competitor keywords display
        columns = ('keyword', 'frequency', 'sites', 'avg_position')
        self.competitor_tree = ttk.Treeview(self.competitor_frame, columns=columns, show='headings', height=15)
        
        # Define column headings and widths
        self.competitor_tree.heading('keyword', text='Keyword')
        self.competitor_tree.heading('frequency', text='Frequency')
        self.competitor_tree.heading('sites', text='Found in Sites')
        self.competitor_tree.heading('avg_position', text='Avg Position')
        
        self.competitor_tree.column('keyword', width=300)
        self.competitor_tree.column('frequency', width=100)
        self.competitor_tree.column('sites', width=100)
        self.competitor_tree.column('avg_position', width=120)
        
        # Scrollbars for competitor tree
        comp_v_scrollbar = ttk.Scrollbar(self.competitor_frame, orient=tk.VERTICAL, command=self.competitor_tree.yview)
        comp_h_scrollbar = ttk.Scrollbar(self.competitor_frame, orient=tk.HORIZONTAL, command=self.competitor_tree.xview)
        self.competitor_tree.configure(yscrollcommand=comp_v_scrollbar.set, xscrollcommand=comp_h_scrollbar.set)
        
        # Grid the treeview and scrollbars
        self.competitor_tree.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        comp_v_scrollbar.grid(row=1, column=1, sticky=(tk.N, tk.S))
        comp_h_scrollbar.grid(row=2, column=0, sticky=(tk.W, tk.E))
        
    def create_missing_keywords_tab(self):
        """Create missing keywords analysis tab"""
        self.missing_frame.columnconfigure(0, weight=1)
        self.missing_frame.rowconfigure(1, weight=1)
        
        # Priority filter
        priority_frame = ttk.Frame(self.missing_frame)
        priority_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        
        ttk.Label(priority_frame, text="Priority Level:").pack(side=tk.LEFT)
        self.priority_var = tk.StringVar(value="all")
        priority_combo = ttk.Combobox(priority_frame, textvariable=self.priority_var, 
                                    values=["all", "high", "medium", "low"], 
                                    state="readonly", width=10)
        priority_combo.pack(side=tk.LEFT, padx=(5, 15))
        priority_combo.bind('<<ComboboxSelected>>', self.filter_missing_keywords)
        
        # Missing keywords display
        missing_columns = ('keyword', 'priority', 'frequency', 'opportunity_score')
        self.missing_tree = ttk.Treeview(self.missing_frame, columns=missing_columns, show='headings', height=15)
        
        # Define column headings
        self.missing_tree.heading('keyword', text='Missing Keyword')
        self.missing_tree.heading('priority', text='Priority')
        self.missing_tree.heading('frequency', text='Competitor Frequency')
        self.missing_tree.heading('opportunity_score', text='Opportunity Score')
        
        self.missing_tree.column('keyword', width=300)
        self.missing_tree.column('priority', width=100)
        self.missing_tree.column('frequency', width=150)
        self.missing_tree.column('opportunity_score', width=150)
        
        # Scrollbars for missing tree
        miss_v_scrollbar = ttk.Scrollbar(self.missing_frame, orient=tk.VERTICAL, command=self.missing_tree.yview)
        miss_h_scrollbar = ttk.Scrollbar(self.missing_frame, orient=tk.HORIZONTAL, command=self.missing_tree.xview)
        self.missing_tree.configure(yscrollcommand=miss_v_scrollbar.set, xscrollcommand=miss_h_scrollbar.set)
        
        # Grid the treeview and scrollbars
        self.missing_tree.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        miss_v_scrollbar.grid(row=1, column=1, sticky=(tk.N, tk.S))
        miss_h_scrollbar.grid(row=2, column=0, sticky=(tk.W, tk.E))
        
    def create_summary_tab(self):
        """Create analysis summary tab"""
        self.summary_frame.columnconfigure(0, weight=1)
        self.summary_frame.rowconfigure(0, weight=1)
        
        # Summary text area
        self.summary_text = scrolledtext.ScrolledText(self.summary_frame, wrap=tk.WORD, 
                                                     height=20, font=('Arial', 10))
        self.summary_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
    def create_report_tab(self):
        """Create detailed report tab"""
        self.report_frame.columnconfigure(0, weight=1)
        self.report_frame.rowconfigure(0, weight=1)
        
        # Report text area
        self.report_text = scrolledtext.ScrolledText(self.report_frame, wrap=tk.WORD, 
                                                    height=20, font=('Consolas', 9))
        self.report_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
    def create_export_section(self, parent):
        """Create export options section"""
        export_frame = ttk.LabelFrame(parent, text="Export Results", padding="10")
        export_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E))
        
        ttk.Button(export_frame, text="📊 Export to CSV", 
                  command=self.export_csv, style='Export.TButton').pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Button(export_frame, text="📄 Export to PDF", 
                  command=self.export_pdf, style='Export.TButton').pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Button(export_frame, text="📋 Copy to Clipboard", 
                  command=self.copy_to_clipboard).pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Button(export_frame, text="💾 Save Session", 
                  command=self.save_session).pack(side=tk.LEFT, padx=(0, 10))
        
    def create_status_bar(self):
        """Create status bar at bottom of window"""
        self.status_frame = ttk.Frame(self.root)
        self.status_frame.grid(row=1, column=0, sticky=(tk.W, tk.E))
        self.status_frame.columnconfigure(1, weight=1)
        
        self.status_label = ttk.Label(self.status_frame, text="Ready for analysis")
        self.status_label.grid(row=0, column=0, sticky=tk.W, padx=(10, 0))
        
        # Analysis time label
        self.time_label = ttk.Label(self.status_frame, text="")
        self.time_label.grid(row=0, column=2, sticky=tk.E, padx=(0, 10))
        
    def start_analysis(self):
        """Start the SEO analysis process"""
        # Validate inputs
        if not self.keyword_var.get().strip():
            messagebox.showerror("Error", "Please enter a target keyword")
            return
            
        if not self.content_var.get().strip():
            messagebox.showerror("Error", "Please provide your content (URL, text, or file)")
            return
        
        # Validate content based on method
        content_method = self.content_method_var.get()
        content_input = self.content_var.get().strip()
        
        if content_method == 'url':
            if not content_input.startswith(('http://', 'https://')):
                messagebox.showerror("Error", "URL must start with http:// or https://")
                return
        elif content_method == 'file':
            if not os.path.exists(content_input):
                messagebox.showerror("Error", f"File not found: {content_input}")
                return
        
        # Validate keyword length
        if len(self.keyword_var.get().strip()) > 100:
            messagebox.showerror("Error", "Keyword is too long (max 100 characters)")
            return
        
        # Disable analyze button and enable stop button
        self.analyze_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        
        # Clear previous results
        self.clear_results()
        
        # Initialize stop flag
        self.stop_requested = False
        
        # Start analysis in separate thread
        self.analysis_thread = threading.Thread(target=self.run_analysis)
        self.analysis_thread.daemon = True
        self.analysis_thread.start()
        
    def run_analysis(self):
        """Run the complete SEO analysis"""
        try:
            from datetime import timezone
            start_time = datetime.now(timezone.utc)
            
            with PerformanceTimer("Complete SEO Analysis"):
                # Update status
                self.update_status("Starting analysis...")
                self.update_progress(5)
                
                # Prepare search query
                keyword = self.keyword_var.get().strip()
                location = self.location_var.get().strip()
                search_query = f"{keyword} {location}" if location else keyword
                
                # Step 1: Scrape Google search results
                self.update_status("Scraping Google search results...")
                self.update_progress(10)
                
                search_results = self.scraper.scrape_google_results(
                    search_query,
                    num_results=self.results_count_var.get()
                )
                
                if not search_results:
                    self.update_status("No search results found")
                    return
                    
                self.update_progress(30)
                
                # Step 2: Extract and analyze competitor content
                self.update_status("Analyzing competitor content...")
                
                all_competitor_text = []
                for i, result in enumerate(search_results):
                    if self.stop_requested:
                        return
                        
                    self.update_status(f"Processing competitor {i+1}/{len(search_results)}...")
                    content = self.scraper.extract_content_from_url(result['url'])
                    if content:
                        all_competitor_text.append(content)
                    self.update_progress(30 + (i * 40 / len(search_results)))
                
                # Step 3: Analyze competitor keywords
                self.update_status("Extracting competitor keywords...")
                self.update_progress(75)
                
                # Get advanced options
                min_freq = self.min_frequency_var.get()
                exclude_common = self.exclude_common_var.get()
                custom_stopwords = self.custom_stopwords_var.get().split(',') if self.custom_stopwords_var.get() else []
                
                self.competitor_keywords = self.analyzer.analyze_multiple_texts(
                    all_competitor_text,
                    min_frequency=min_freq,
                    exclude_common_words=exclude_common,
                    custom_stopwords=custom_stopwords
                )
                
                # Step 4: Analyze user content
                self.update_status("Analyzing your content...")
                self.update_progress(85)
                
                user_content = self.get_user_content()
                if user_content:
                    self.user_content_keywords = self.analyzer.analyze_text(
                        user_content,
                        min_frequency=1,  # Lower threshold for user content
                        exclude_common_words=exclude_common,
                        custom_stopwords=custom_stopwords
                    )
                
                # Step 5: Find content gaps
                self.update_status("Identifying content gaps...")
                self.update_progress(95)
                
                self.missing_keywords = self.gap_finder.find_missing_keywords(
                    self.competitor_keywords,
                    self.user_content_keywords
                )
                
                # Step 6: Update GUI with results
                self.update_status("Updating results...")
                self.root.after(0, self.display_results)
                
                # Calculate analysis time
                from datetime import timezone
                end_time = datetime.now(timezone.utc)
                analysis_time = (end_time - start_time).total_seconds()
                
                self.root.after(0, lambda: self.time_label.config(
                    text=f"Analysis completed in {analysis_time:.1f} seconds"
                ))
                
                self.update_progress(100)
                self.update_status("Analysis completed successfully!")
            
        except requests.RequestException as e:
            self.root.after(0, lambda: messagebox.showerror("Network Error", f"Failed to connect to websites. Please check your internet connection.\n\nDetails: {str(e)}"))
            self.update_status("Analysis failed: Network error")
        except FileNotFoundError as e:
            self.root.after(0, lambda: messagebox.showerror("File Error", f"File not found: {str(e)}"))
            self.update_status("Analysis failed: File not found")
        except PermissionError as e:
            self.root.after(0, lambda: messagebox.showerror("Permission Error", f"Permission denied: {str(e)}"))
            self.update_status("Analysis failed: Permission denied")
        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror("Analysis Error", f"An unexpected error occurred:\n\n{str(e)}"))
            self.update_status(f"Analysis failed: {str(e)}")
        finally:
            # Re-enable analyze button and disable stop button
            self.root.after(0, lambda: self.analyze_button.config(state=tk.NORMAL))
            self.root.after(0, lambda: self.stop_button.config(state=tk.DISABLED))
            
    def get_user_content(self):
        """Get user content based on selected method"""
        method = self.content_method_var.get()
        content_input = self.content_var.get().strip()
        
        if method == "url":
            return self.scraper.extract_content_from_url(content_input)
        elif method == "text":
            return content_input
        elif method == "file":
            try:
                with open(content_input, 'r', encoding='utf-8') as file:
                    return file.read()
            except Exception as e:
                messagebox.showerror("File Error", f"Could not read file: {str(e)}")
                return None
        
        return None
        
    def display_results(self):
        """Display analysis results in the GUI"""
        # Clear existing results
        for item in self.competitor_tree.get_children():
            self.competitor_tree.delete(item)
        for item in self.missing_tree.get_children():
            self.missing_tree.delete(item)
            
        # Cache sorted results for performance
        if not hasattr(self, '_sorted_competitor_keywords'):
            self._sorted_competitor_keywords = sorted(self.competitor_keywords.items(), 
                                                     key=lambda x: x[1]['frequency'], reverse=True)
        
        if not hasattr(self, '_sorted_missing_keywords'):
            self._sorted_missing_keywords = sorted(self.missing_keywords, 
                                                  key=lambda x: x['opportunity_score'], reverse=True)
            
        # Display competitor keywords
        for keyword, data in self._sorted_competitor_keywords:
            self.competitor_tree.insert('', 'end', values=(
                keyword,
                data['frequency'],
                len(data.get('sources', [])),
                f"{data.get('avg_position', 0):.1f}"
            ))
        
        # Display missing keywords
        for keyword_data in self._sorted_missing_keywords:
            self.missing_tree.insert('', 'end', values=(
                keyword_data['keyword'],
                keyword_data['priority'],
                keyword_data['competitor_frequency'],
                f"{keyword_data['opportunity_score']:.1f}"
            ))
        
        # Generate and display summary
        self.generate_summary()
        
        # Generate and display detailed report
        self.generate_detailed_report()
        
    def generate_summary(self):
        """Generate analysis summary"""
        summary = []
        summary.append("=== SEO CONTENT GAP ANALYSIS SUMMARY ===\n")
        summary.append(f"Target Keyword: {self.keyword_var.get()}")
        
        if self.location_var.get():
            summary.append(f"Location: {self.location_var.get()}")
            
        summary.append(f"Analysis Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        
        # Competitor analysis summary
        summary.append("COMPETITOR ANALYSIS:")
        summary.append(f"• Total unique keywords found: {len(self.competitor_keywords)}")
        
        if self.competitor_keywords:
            top_keywords = sorted(self.competitor_keywords.items(), 
                                key=lambda x: x[1]['frequency'], reverse=True)[:10]
            summary.append(f"• Most frequent competitor keyword: '{top_keywords[0][0]}' ({top_keywords[0][1]['frequency']} occurrences)")
            
        # Content gap analysis
        summary.append(f"\nCONTENT GAP ANALYSIS:")
        summary.append(f"• Missing keywords identified: {len(self.missing_keywords)}")
        
        if self.missing_keywords:
            high_priority = [k for k in self.missing_keywords if k['priority'] == 'high']
            medium_priority = [k for k in self.missing_keywords if k['priority'] == 'medium']
            low_priority = [k for k in self.missing_keywords if k['priority'] == 'low']
            
            summary.append(f"• High priority opportunities: {len(high_priority)}")
            summary.append(f"• Medium priority opportunities: {len(medium_priority)}")
            summary.append(f"• Low priority opportunities: {len(low_priority)}")
            
            if high_priority:
                summary.append(f"\nTOP OPPORTUNITIES:")
                for i, keyword_data in enumerate(high_priority[:5], 1):
                    summary.append(f"{i}. {keyword_data['keyword']} (Score: {keyword_data['opportunity_score']:.1f})")
        
        # Recommendations
        summary.append(f"\nRECOMMENDations:")
        summary.append("• Focus on high-priority missing keywords first")
        summary.append("• Create content targeting top opportunity keywords")
        summary.append("• Monitor competitor content for new keyword trends")
        summary.append("• Regularly update your content with identified keywords")
        
        self.summary_text.delete(1.0, tk.END)
        self.summary_text.insert(1.0, '\n'.join(summary))
        
    def generate_detailed_report(self):
        """Generate detailed analysis report"""
        report = []
        report.append("=== DETAILED SEO ANALYSIS REPORT ===\n")
        
        # Configuration details
        report.append("ANALYSIS CONFIGURATION:")
        report.append(f"Target Keyword: {self.keyword_var.get()}")
        report.append(f"Location: {self.location_var.get() or 'Not specified'}")
        report.append(f"Results Analyzed: {self.results_count_var.get()}")
        report.append(f"Min Keyword Frequency: {self.min_frequency_var.get()}")
        report.append(f"Exclude Common Words: {'Yes' if self.exclude_common_var.get() else 'No'}")
        
        if self.custom_stopwords_var.get():
            report.append(f"Custom Stopwords: {self.custom_stopwords_var.get()}")
        report.append("")
        
        # Competitor keywords analysis
        report.append("COMPETITOR KEYWORDS ANALYSIS:")
        report.append(f"{'Keyword':<30} {'Frequency':<10} {'Sites':<8} {'Avg Pos':<8}")
        report.append("-" * 60)
        
        for keyword, data in sorted(self.competitor_keywords.items(), 
                                   key=lambda x: x[1]['frequency'], reverse=True)[:20]:
            report.append(f"{keyword:<30} {data['frequency']:<10} {len(data.get('sources', [])):<8} {data.get('avg_position', 0):<8.1f}")
        
        report.append("")
        
        # Missing keywords analysis
        report.append("MISSING KEYWORDS ANALYSIS:")
        report.append(f"{'Keyword':<30} {'Priority':<10} {'Comp Freq':<10} {'Score':<8}")
        report.append("-" * 60)
        
        for keyword_data in sorted(self.missing_keywords, 
                                  key=lambda x: x['opportunity_score'], reverse=True)[:20]:
            report.append(f"{keyword_data['keyword']:<30} {keyword_data['priority']:<10} {keyword_data['competitor_frequency']:<10} {keyword_data['opportunity_score']:<8.1f}")
        
        self.report_text.delete(1.0, tk.END)
        self.report_text.insert(1.0, '\n'.join(report))
        
    def filter_competitor_keywords(self):
        """Filter competitor keywords based on frequency"""
        min_freq = self.freq_filter_var.get()
        
        # Clear existing items
        for item in self.competitor_tree.get_children():
            self.competitor_tree.delete(item)
            
        # Re-populate with filtered data
        for keyword, data in sorted(self.competitor_keywords.items(), 
                                   key=lambda x: x[1]['frequency'], reverse=True):
            if data['frequency'] >= min_freq:
                self.competitor_tree.insert('', 'end', values=(
                    keyword,
                    data['frequency'],
                    len(data.get('sources', [])),
                    f"{data.get('avg_position', 0):.1f}"
                ))
        
    def search_keywords(self, event):
        """Search keywords in real-time"""
        search_term = self.keyword_search_var.get().lower()
        
        # Clear existing items
        for item in self.competitor_tree.get_children():
            self.competitor_tree.delete(item)
            
        # Re-populate with filtered data
        for keyword, data in sorted(self.competitor_keywords.items(), 
                                   key=lambda x: x[1]['frequency'], reverse=True):
            if not search_term or search_term in keyword.lower():
                self.competitor_tree.insert('', 'end', values=(
                    keyword,
                    data['frequency'],
                    len(data.get('sources', [])),
                    f"{data.get('avg_position', 0):.1f}"
                ))
        
    def filter_missing_keywords(self, event):
        """Filter missing keywords by priority"""
        priority_filter = self.priority_var.get()
        
        # Clear existing items
        for item in self.missing_tree.get_children():
            self.missing_tree.delete(item)
            
        # Re-populate with filtered data
        for keyword_data in sorted(self.missing_keywords, 
                                  key=lambda x: x['opportunity_score'], reverse=True):
            if priority_filter == "all" or keyword_data['priority'] == priority_filter:
                self.missing_tree.insert('', 'end', values=(
                    keyword_data['keyword'],
                    keyword_data['priority'],
                    keyword_data['competitor_frequency'],
                    f"{keyword_data['opportunity_score']:.1f}"
                ))
        
    def stop_analysis(self):
        """Stop the current analysis"""
        self.update_status("Stopping analysis...")
        if hasattr(self, 'analysis_thread') and self.analysis_thread.is_alive():
            # Set a flag to stop the analysis
            self.stop_requested = True
            self.analyze_button.config(state=tk.NORMAL)
            self.stop_button.config(state=tk.DISABLED)
            self.update_status("Analysis stopped by user")
        
    def clear_results(self):
        """Clear all analysis results"""
        # Clear treeviews
        for item in self.competitor_tree.get_children():
            self.competitor_tree.delete(item)
        for item in self.missing_tree.get_children():
            self.missing_tree.delete(item)
            
        # Clear text areas
        self.summary_text.delete(1.0, tk.END)
        self.report_text.delete(1.0, tk.END)
        
        # Reset data
        self.current_results = {}
        self.competitor_keywords = {}
        self.user_content_keywords = {}
        self.missing_keywords = []
        
        # Clear cached sorted results
        if hasattr(self, '_sorted_competitor_keywords'):
            delattr(self, '_sorted_competitor_keywords')
        if hasattr(self, '_sorted_missing_keywords'):
            delattr(self, '_sorted_missing_keywords')
        
        # Reset progress
        self.update_progress(0)
        self.update_status("Results cleared")
        
    def export_csv(self):
        """Export results to CSV"""
        if not self.competitor_keywords and not self.missing_keywords:
            messagebox.showwarning("No Data", "No analysis results to export")
            return
            
        filename = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
            title="Export Results to CSV"
        )
        
        if filename:
            try:
                self.exporter.export_to_csv(
                    filename,
                    self.competitor_keywords,
                    self.missing_keywords,
                    {
                        'keyword': self.keyword_var.get(),
                        'location': self.location_var.get(),
                        'analysis_date': datetime.now().isoformat()
                    }
                )
                messagebox.showinfo("Export Successful", f"Results exported to {filename}")
            except PermissionError as e:
                messagebox.showerror("Permission Error", f"Cannot write to file. Please check file permissions.\n\nDetails: {str(e)}")
            except FileNotFoundError as e:
                messagebox.showerror("File Error", f"Directory not found. Please check the path.\n\nDetails: {str(e)}")
            except Exception as e:
                messagebox.showerror("Export Error", f"Failed to export: {str(e)}")
                
    def export_pdf(self):
        """Export results to PDF"""
        if not self.competitor_keywords and not self.missing_keywords:
            messagebox.showwarning("No Data", "No analysis results to export")
            return
            
        filename = filedialog.asksaveasfilename(
            defaultextension=".pdf",
            filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")],
            title="Export Results to PDF"
        )
        
        if filename:
            try:
                self.exporter.export_to_pdf(
                    filename,
                    self.competitor_keywords,
                    self.missing_keywords,
                    {
                        'keyword': self.keyword_var.get(),
                        'location': self.location_var.get(),
                        'analysis_date': datetime.now().isoformat()
                    }
                )
                messagebox.showinfo("Export Successful", f"Results exported to {filename}")
            except PermissionError as e:
                messagebox.showerror("Permission Error", f"Cannot write to file. Please check file permissions.\n\nDetails: {str(e)}")
            except FileNotFoundError as e:
                messagebox.showerror("File Error", f"Directory not found. Please check the path.\n\nDetails: {str(e)}")
            except Exception as e:
                messagebox.showerror("Export Error", f"Failed to export: {str(e)}")
                
    def copy_to_clipboard(self):
        """Copy results to clipboard"""
        # Implementation for clipboard copy
        summary_text = self.summary_text.get(1.0, tk.END)
        self.root.clipboard_clear()
        self.root.clipboard_append(summary_text)
        messagebox.showinfo("Copied", "Results copied to clipboard")
        
    def save_session(self):
        """Save current session data"""
        filename = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
            title="Save Session"
        )
        
        if filename:
            try:
                session_data = {
                    'keyword': self.keyword_var.get(),
                    'location': self.location_var.get(),
                    'content_method': self.content_method_var.get(),
                    'content': self.content_var.get(),
                    'competitor_keywords': self.competitor_keywords,
                    'missing_keywords': self.missing_keywords,
                    'analysis_date': datetime.now().isoformat()
                }
                
                with open(filename, 'w') as f:
                    json.dump(session_data, f, indent=2)
                    
                messagebox.showinfo("Session Saved", f"Session saved to {filename}")
            except PermissionError as e:
                messagebox.showerror("Permission Error", f"Cannot write to file. Please check file permissions.\n\nDetails: {str(e)}")
            except Exception as e:
                messagebox.showerror("Save Error", f"Failed to save session: {str(e)}")
                
    def load_session(self):
        """Load previous session if exists"""
        session_file = "last_session.json"
        if os.path.exists(session_file):
            try:
                with open(session_file, 'r') as f:
                    session_data = json.load(f)
                    
                # Restore session data
                self.keyword_var.set(session_data.get('keyword', ''))
                self.location_var.set(session_data.get('location', ''))
                self.content_method_var.set(session_data.get('content_method', 'url'))
                self.content_var.set(session_data.get('content', ''))
                
            except Exception:
                pass  # Ignore errors loading session
                
    def update_status(self, message):
        """Update status label"""
        def update():
            self.status_label.config(text=message)
        self.root.after(0, update)
        
    def update_progress(self, value):
        """Update progress bar"""
        def update():
            self.progress_var.set(value)
        self.root.after(0, update)
        
    # Menu command implementations
    def new_analysis(self):
        """Start new analysis"""
        self.clear_results()
        
    def save_results(self):
        """Save current results"""
        self.save_session()
        
    def load_results(self):
        """Load saved results"""
        filename = filedialog.askopenfilename(
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
            title="Load Session"
        )
        
        if filename:
            try:
                with open(filename, 'r') as f:
                    session_data = json.load(f)
                    
                # Restore session data
                self.keyword_var.set(session_data.get('keyword', ''))
                self.location_var.set(session_data.get('location', ''))
                self.competitor_keywords = session_data.get('competitor_keywords', {})
                self.missing_keywords = session_data.get('missing_keywords', [])
                
                # Display loaded results
                self.display_results()
                
                messagebox.showinfo("Session Loaded", "Session loaded successfully")
            except FileNotFoundError as e:
                messagebox.showerror("File Error", f"Session file not found: {str(e)}")
            except json.JSONDecodeError as e:
                messagebox.showerror("File Error", f"Invalid session file format: {str(e)}")
            except Exception as e:
                messagebox.showerror("Load Error", f"Failed to load session: {str(e)}")
                
    def open_settings(self):
        """Open settings dialog"""
        messagebox.showinfo("Settings", "Settings dialog would open here")
        
    def show_history(self):
        """Show keyword analysis history"""
        messagebox.showinfo("History", "Keyword history would be displayed here")
        
    def batch_analysis(self):
        """Open batch analysis dialog"""
        messagebox.showinfo("Batch Analysis", "Batch analysis dialog would open here")
        
    def show_help(self):
        """Show help documentation"""
        help_text = """
        SEO RANK & CONTENT GAP ANALYZER HELP
        
        1. Enter your target keyword and optional location
        2. Specify your content (URL, text, or file)
        3. Configure advanced options if needed
        4. Click 'Start Analysis' to begin
        5. Review results in the tabs below
        6. Export results as needed
        
        For more detailed help, visit our documentation.
        """
        messagebox.showinfo("Help", help_text)
        
    def show_api_docs(self):
        """Show API documentation"""
        webbrowser.open("https://developers.google.com/custom-search/v1/overview")
        
    def show_about(self):
        """Show about dialog"""
        about_text = """
        SEO Rank & Content Gap Analyzer Pro
        Version 1.0.0
        
        A professional tool for SEO content gap analysis
        and competitor keyword research.
        
        © 2025 Your Company Name
        """
        messagebox.showinfo("About", about_text)

def main():
    root = tk.Tk()
    app = SEOAnalyzerGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()