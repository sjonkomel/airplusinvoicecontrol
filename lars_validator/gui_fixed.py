#!/usr/bin/env python3
"""
LARS File Validator and Repair Tool - Fixed GUI
==============================================

Simplified and corrected GUI version that avoids the Tkinter layout issues.
Now supports .lrs file extension.
"""

import os
import sys
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
from pathlib import Path

# Ensure we can import from the current directory
sys.path.insert(0, str(Path(__file__).parent))

from main import LARSValidator, LARSFile, ValidationError, ErrorSeverity


class LARSValidatorGUI:
    """Main GUI application for LARS file validation and repair"""
    
    def __init__(self, root: tk.Tk):
        self.root = root
        self.validator = LARSValidator()
        self.current_file: LARSFile = None
        self.current_file_path: str = None
        self.fixed_file: LARSFile = None
        
        self.setup_ui()
        self.update_title()
    
    def setup_ui(self):
        """Set up the user interface"""
        self.root.title("LARS File Validator and Repair Tool")
        self.root.geometry("1000x700")
        self.root.minsize(800, 500)
        
        # Create main container
        self.main_frame = ttk.Frame(self.root, padding="10")
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create notebook for tabs
        self.notebook = ttk.Notebook(self.main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # Create tabs
        self.setup_file_tab()
        self.setup_validation_tab()
        self.setup_repair_tab()
        self.setup_export_tab()
        self.setup_help_tab()
        
        # Status bar
        self.status_var = tk.StringVar()
        self.status_var.set("Ready")
        self.status_bar = ttk.Label(
            self.main_frame, 
            textvariable=self.status_var, 
            relief=tk.SUNKEN,
            anchor=tk.W
        )
        self.status_bar.pack(fill=tk.X, pady=(5, 0))
    
    def setup_file_tab(self):
        """Set up the file upload tab"""
        file_frame = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(file_frame, text="File")
        
        # File selection frame
        selection_frame = ttk.LabelFrame(file_frame, text="File Selection", padding="10")
        selection_frame.pack(fill=tk.X, pady=5)
        
        # File path entry
        self.file_path_var = tk.StringVar()
        file_entry_frame = ttk.Frame(selection_frame)
        file_entry_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(file_entry_frame, text="File:").pack(side=tk.LEFT)
        self.file_entry = ttk.Entry(file_entry_frame, textvariable=self.file_path_var, width=50)
        self.file_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        # Browse button
        browse_btn = ttk.Button(
            file_entry_frame, 
            text="Browse...", 
            command=self.browse_file
        )
        browse_btn.pack(side=tk.LEFT)
        
        # File info frame
        info_frame = ttk.LabelFrame(file_frame, text="File Information", padding="10")
        info_frame.pack(fill=tk.X, pady=5)
        
        # File info labels
        info_fields = [
            ("Version:", "version"),
            ("Total Records:", "total_records"),
            ("Valid Records:", "valid_records"),
            ("Invalid Records:", "invalid_records"),
            ("Total Errors:", "total_errors"),
            ("Critical Errors:", "critical_errors"),
            ("Errors:", "errors"),
            ("Warnings:", "warnings"),
            ("Auto-fixable:", "auto_fixable"),
        ]
        
        self.info_vars = {}
        for i, (label_text, field_name) in enumerate(info_fields):
            row = i // 4
            col = i % 4
            
            ttk.Label(info_frame, text=label_text).grid(
                row=row, column=col*2, sticky=tk.W, padx=5, pady=2
            )
            value_var = tk.StringVar(value="-")
            self.info_vars[field_name] = value_var
            ttk.Label(info_frame, textvariable=value_var).grid(
                row=row, column=col*2+1, sticky=tk.W, padx=5, pady=2
            )
        
        # Action buttons
        action_frame = ttk.Frame(file_frame)
        action_frame.pack(fill=tk.X, pady=10)
        
        self.parse_btn = ttk.Button(
            action_frame,
            text="Parse File",
            command=self.parse_file,
            state=tk.DISABLED
        )
        self.parse_btn.pack(side=tk.LEFT, padx=5)
        
        self.validate_btn = ttk.Button(
            action_frame,
            text="Validate",
            command=self.validate_file,
            state=tk.DISABLED
        )
        self.validate_btn.pack(side=tk.LEFT, padx=5)
        
        self.clear_btn = ttk.Button(
            action_frame,
            text="Clear",
            command=self.clear_file
        )
        self.clear_btn.pack(side=tk.RIGHT, padx=5)
    
    def setup_validation_tab(self):
        """Set up the validation results tab"""
        validation_frame = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(validation_frame, text="Validation Results")
        
        # Summary frame
        summary_frame = ttk.LabelFrame(validation_frame, text="Summary", padding="10")
        summary_frame.pack(fill=tk.X, pady=5)
        
        self.summary_text = scrolledtext.ScrolledText(
            summary_frame, 
            height=8, 
            wrap=tk.WORD,
            state=tk.DISABLED
        )
        self.summary_text.pack(fill=tk.BOTH, expand=True)
        
        # Errors frame
        errors_frame = ttk.LabelFrame(validation_frame, text="Errors and Warnings", padding="10")
        errors_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # Treeview for errors
        self.errors_tree = ttk.Treeview(errors_frame, columns=(
            'line', 'severity', 'type', 'field', 'message', 'fixable'
        ), show='headings')
        
        self.errors_tree.heading('line', text='Line')
        self.errors_tree.heading('severity', text='Severity')
        self.errors_tree.heading('type', text='Type')
        self.errors_tree.heading('field', text='Field')
        self.errors_tree.heading('message', text='Message')
        self.errors_tree.heading('fixable', text='Auto-fix')
        
        self.errors_tree.column('line', width=60, anchor=tk.CENTER)
        self.errors_tree.column('severity', width=80, anchor=tk.CENTER)
        self.errors_tree.column('type', width=120, anchor=tk.W)
        self.errors_tree.column('field', width=100, anchor=tk.W)
        self.errors_tree.column('message', width=300, anchor=tk.W)
        self.errors_tree.column('fixable', width=60, anchor=tk.CENTER)
        
        self.errors_tree.pack(fill=tk.BOTH, expand=True)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(
            errors_frame, 
            orient=tk.VERTICAL, 
            command=self.errors_tree.yview
        )
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.errors_tree.configure(yscrollcommand=scrollbar.set)
        
        # Filter frame
        filter_frame = ttk.Frame(errors_frame)
        filter_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(filter_frame, text="Filter:").pack(side=tk.LEFT)
        self.filter_var = tk.StringVar(value="all")
        filter_combo = ttk.Combobox(
            filter_frame, 
            textvariable=self.filter_var,
            values=["all", "critical", "error", "warning", "info", "fixable"],
            state="readonly",
            width=10
        )
        filter_combo.pack(side=tk.LEFT, padx=5)
        filter_combo.bind("<<ComboboxSelected>>", self.filter_errors)
        
        # Export errors button
        export_btn = ttk.Button(
            filter_frame,
            text="Export Errors",
            command=self.export_errors
        )
        export_btn.pack(side=tk.RIGHT, padx=5)
    
    def setup_repair_tab(self):
        """Set up the repair tab"""
        repair_frame = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(repair_frame, text="Repair")
        
        # Instructions
        instructions = ttk.Label(
            repair_frame,
            text="Review the validation errors and apply automatic fixes where possible.",
            wraplength=800
        )
        instructions.pack(pady=10)
        
        # Auto-fix frame
        auto_fix_frame = ttk.LabelFrame(repair_frame, text="Automatic Fixes", padding="10")
        auto_fix_frame.pack(fill=tk.X, pady=5)
        
        self.fixes_text = scrolledtext.ScrolledText(
            auto_fix_frame,
            height=10,
            wrap=tk.WORD,
            state=tk.DISABLED
        )
        self.fixes_text.pack(fill=tk.BOTH, expand=True)
        
        # Action buttons
        action_frame = ttk.Frame(auto_fix_frame)
        action_frame.pack(fill=tk.X, pady=5)
        
        self.apply_fixes_btn = ttk.Button(
            action_frame,
            text="Apply Auto-Fixes",
            command=self.apply_auto_fixes,
            state=tk.DISABLED
        )
        self.apply_fixes_btn.pack(side=tk.LEFT, padx=5)
        
        self.undo_fixes_btn = ttk.Button(
            action_frame,
            text="Undo Fixes",
            command=self.undo_fixes,
            state=tk.DISABLED
        )
        self.undo_fixes_btn.pack(side=tk.LEFT, padx=5)
    
    def setup_export_tab(self):
        """Set up the export tab"""
        export_frame = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(export_frame, text="Export")
        
        # Instructions
        instructions = ttk.Label(
            export_frame,
            text="Export the validated and repaired LARS file for use in your ERP system.",
            wraplength=800
        )
        instructions.pack(pady=10)
        
        # Export options
        options_frame = ttk.LabelFrame(export_frame, text="Export Options", padding="10")
        options_frame.pack(fill=tk.X, pady=5)
        
        # Export as
        ttk.Label(options_frame, text="Export as:").pack(anchor=tk.W, pady=2)
        self.export_as_var = tk.StringVar(value="original")
        ttk.Radiobutton(
            options_frame, 
            text="Original file (with fixes)", 
            variable=self.export_as_var, 
            value="original"
        ).pack(anchor=tk.W, padx=20, pady=2)
        ttk.Radiobutton(
            options_frame, 
            text="New file", 
            variable=self.export_as_var, 
            value="new"
        ).pack(anchor=tk.W, padx=20, pady=2)
        
        # Output file
        output_frame = ttk.Frame(options_frame)
        output_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(output_frame, text="Output file:").pack(side=tk.LEFT)
        self.output_path_var = tk.StringVar()
        self.output_entry = ttk.Entry(output_frame, textvariable=self.output_path_var, width=40)
        self.output_entry.pack(side=tk.LEFT, padx=5)
        
        output_browse_btn = ttk.Button(
            output_frame,
            text="Browse...",
            command=self.browse_output_file
        )
        output_browse_btn.pack(side=tk.LEFT)
        
        # Export button
        export_btn = ttk.Button(
            options_frame,
            text="Export File",
            command=self.export_file,
            state=tk.DISABLED
        )
        export_btn.pack(pady=10)
        self.export_btn = export_btn
        
        # Export summary
        summary_frame = ttk.LabelFrame(export_frame, text="Export Summary", padding="10")
        summary_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        self.export_summary_text = scrolledtext.ScrolledText(
            summary_frame,
            height=10,
            wrap=tk.WORD,
            state=tk.DISABLED
        )
        self.export_summary_text.pack(fill=tk.BOTH, expand=True)
    
    def setup_help_tab(self):
        """Set up the help tab"""
        help_frame = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(help_frame, text="Help")
        
        help_text = """
LARS File Validator and Repair Tool

This application helps you validate and repair AIRPLUS LARS/LRS invoice files before uploading them to your ERP system.

FEATURES:
- Upload and parse LARS/LRS files
- Automatic detection of file format errors
- Interactive error review and repair
- Automatic fixes for common issues
- Export corrected files for ERP upload

HOW TO USE:
1. Select a LARS/LRS file using the Browse button
2. Click "Parse File" to load and parse the file
3. Click "Validate" to check for errors
4. Review errors in the Validation Results tab
5. Apply automatic fixes in the Repair tab
6. Export the corrected file in the Export tab

SUPPORTED FILE TYPES:
- .txt (Text files)
- .lars (LARS files)
- .lrs (LRS files)
- .dat (Data files)
- Any other text-based files

For command line usage, see the CLI documentation.
        """
        
        help_text_widget = scrolledtext.ScrolledText(
            help_frame,
            height=20,
            wrap=tk.WORD,
            state=tk.NORMAL
        )
        help_text_widget.insert(tk.END, help_text)
        help_text_widget.config(state=tk.DISABLED)
        help_text_widget.pack(fill=tk.BOTH, expand=True)
    
    def update_title(self):
        """Update the window title"""
        title = "LARS File Validator and Repair Tool"
        if self.current_file_path:
            title += f" - {os.path.basename(self.current_file_path)}"
        self.root.title(title)
    
    def browse_file(self):
        """Open file dialog to select a LARS/LRS file"""
        file_path = filedialog.askopenfilename(
            title="Select LARS/LRS File",
            filetypes=[
                ("LARS/LRS Files", "*.txt;*.lars;*.lrs;*.dat"),
                ("Text Files", "*.txt"),
                ("All Files", "*.*")
            ]
        )
        
        if file_path:
            self.file_path_var.set(file_path)
            self.current_file_path = file_path
            self.parse_btn.config(state=tk.NORMAL)
            self.update_title()
    
    def browse_output_file(self):
        """Open file dialog to select output file"""
        if not self.current_file_path:
            messagebox.showwarning("No File", "Please select a file first")
            return
        
        default_name = os.path.splitext(os.path.basename(self.current_file_path))[0] + "_fixed.txt"
        file_path = filedialog.asksaveasfilename(
            title="Save Fixed LARS File",
            defaultextension=".txt",
            initialfile=default_name,
            filetypes=[
                ("LARS/LRS Files", "*.txt;*.lars;*.lrs;*.dat"),
                ("Text Files", "*.txt"),
                ("All Files", "*.*")
            ]
        )
        
        if file_path:
            self.output_path_var.set(file_path)
    
    def parse_file(self):
        """Parse the selected LARS file"""
        if not self.current_file_path:
            messagebox.showwarning("No File", "Please select a file first")
            return
        
        try:
            self.status_var.set("Parsing file...")
            self.root.update()
            
            # Parse the file
            self.current_file = self.validator.parse_file(self.current_file_path)
            
            # Update UI
            self.validate_btn.config(state=tk.NORMAL)
            self.status_var.set(f"File parsed: {len(self.current_file.records)} records found")
            
            # Show basic info
            self.update_file_info()
            
            # Enable validation tab
            self.notebook.tab(1, state=tk.NORMAL)  # Validation tab
            self.notebook.tab(2, state=tk.NORMAL)  # Repair tab
            self.notebook.tab(3, state=tk.NORMAL)  # Export tab
            
        except Exception as e:
            messagebox.showerror("Parse Error", f"Error parsing file: {str(e)}")
            self.status_var.set("Error parsing file")
    
    def validate_file(self):
        """Validate the parsed LARS file"""
        if not self.current_file:
            messagebox.showwarning("No File", "Please parse a file first")
            return
        
        try:
            self.status_var.set("Validating file...")
            self.root.update()
            
            # Validate the file
            errors = self.validator.validate_file(self.current_file)
            
            # Update UI
            self.update_file_info()
            self.display_validation_results()
            
            # Enable repair buttons if there are auto-fixable errors
            auto_fixable = len([e for e in errors if e.can_auto_fix])
            if auto_fixable > 0:
                self.apply_fixes_btn.config(state=tk.NORMAL)
            
            # Enable export button
            self.export_btn.config(state=tk.NORMAL)
            
            self.status_var.set(f"Validation complete: {len(errors)} errors found")
            
        except Exception as e:
            messagebox.showerror("Validation Error", f"Error validating file: {str(e)}")
            self.status_var.set("Error validating file")
    
    def update_file_info(self):
        """Update the file information display"""
        if not self.current_file:
            return
        
        summary = self.validator.get_summary(self.current_file)
        
        # Update info labels
        info_mapping = {
            'version': summary.get('version', '-'),
            'total_records': summary.get('total_records', 0),
            'valid_records': summary.get('valid_records', 0),
            'invalid_records': summary.get('invalid_records', 0),
            'total_errors': summary.get('total_errors', 0),
            'critical_errors': summary.get('errors_by_severity', {}).get('critical', 0),
            'errors': summary.get('errors_by_severity', {}).get('error', 0),
            'warnings': summary.get('errors_by_severity', {}).get('warning', 0),
            'auto_fixable': summary.get('auto_fixable_errors', 0),
        }
        
        for field, value in info_mapping.items():
            if field in self.info_vars:
                self.info_vars[field].set(str(value))
    
    def display_validation_results(self):
        """Display validation results in the treeview"""
        if not self.current_file:
            return
        
        # Clear existing items
        for item in self.errors_tree.get_children():
            self.errors_tree.delete(item)
        
        # Add errors to treeview
        for error in self.current_file.validation_errors:
            severity_color = {
                ErrorSeverity.CRITICAL: 'red',
                ErrorSeverity.ERROR: 'red',
                ErrorSeverity.WARNING: 'orange',
                ErrorSeverity.INFO: 'blue'
            }.get(error.severity, 'black')
            
            fixable = "Yes" if error.can_auto_fix else "No"
            
            self.errors_tree.insert('', tk.END, values=(
                error.line_number,
                error.severity.value.upper(),
                error.error_type,
                error.field_name,
                error.message,
                fixable
            ), tags=(error.severity.value,))
        
        # Configure tags for coloring
        self.errors_tree.tag_configure('critical', foreground='red')
        self.errors_tree.tag_configure('error', foreground='red')
        self.errors_tree.tag_configure('warning', foreground='orange')
        self.errors_tree.tag_configure('info', foreground='blue')
        
        # Update summary text
        summary = self.validator.get_summary(self.current_file)
        summary_text = f"""File Validation Summary
======================

Version: {summary.get('version', 'Unknown')}
Total Records: {summary.get('total_records', 0)}
Valid Records: {summary.get('valid_records', 0)}
Invalid Records: {summary.get('invalid_records', 0)}

Error Breakdown:
- Critical: {summary.get('errors_by_severity', {}).get('critical', 0)}
- Errors: {summary.get('errors_by_severity', {}).get('error', 0)}
- Warnings: {summary.get('errors_by_severity', {}).get('warning', 0)}
- Info: {summary.get('errors_by_severity', {}).get('info', 0)}

Auto-fixable Errors: {summary.get('auto_fixable_errors', 0)}

File Status: {"PASS" if summary.get('total_errors', 0) == 0 else "FAIL"}
"""
        
        self.summary_text.config(state=tk.NORMAL)
        self.summary_text.delete(1.0, tk.END)
        self.summary_text.insert(tk.END, summary_text)
        self.summary_text.config(state=tk.DISABLED)
    
    def filter_errors(self, event=None):
        """Filter errors based on selection"""
        filter_type = self.filter_var.get()
        
        for item in self.errors_tree.get_children():
            values = self.errors_tree.item(item, 'values')
            severity = values[1].lower() if values else ''
            fixable = values[5].lower() == 'yes' if values else False
            
            show = True
            if filter_type == 'all':
                show = True
            elif filter_type == 'fixable':
                show = fixable
            else:
                show = severity == filter_type
            
            if show:
                self.errors_tree.item(item, tags=('show',))
            else:
                self.errors_tree.item(item, tags=('hide',))
        
        # Configure tags
        self.errors_tree.tag_configure('show', )
        self.errors_tree.tag_configure('hide', )
    
    def export_errors(self):
        """Export errors to a text file"""
        if not self.current_file:
            messagebox.showwarning("No Errors", "No validation errors to export")
            return
        
        file_path = filedialog.asksaveasfilename(
            title="Save Errors",
            defaultextension=".txt",
            filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")]
        )
        
        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write("LARS File Validation Errors\n")
                    f.write("=" * 50 + "\n\n")
                    
                    for error in self.current_file.validation_errors:
                        f.write(f"Line {error.line_number}\n")
                        f.write(f"  Field: {error.field_name}\n")
                        f.write(f"  Type: {error.error_type}\n")
                        f.write(f"  Severity: {error.severity.value}\n")
                        f.write(f"  Message: {error.message}\n")
                        if error.expected_value:
                            f.write(f"  Expected: {error.expected_value}\n")
                        if error.actual_value:
                            f.write(f"  Actual: {error.actual_value}\n")
                        if error.can_auto_fix:
                            f.write(f"  Auto-fix: Yes ({error.suggested_fix})\n")
                        else:
                            f.write(f"  Auto-fix: No\n")
                        f.write("\n")
                
                messagebox.showinfo("Success", f"Errors exported to {file_path}")
                
            except Exception as e:
                messagebox.showerror("Export Error", f"Error exporting errors: {str(e)}")
    
    def apply_auto_fixes(self):
        """Apply automatic fixes to the file"""
        if not self.current_file:
            messagebox.showwarning("No File", "Please validate a file first")
            return
        
        try:
            self.status_var.set("Applying automatic fixes...")
            self.root.update()
            
            # Apply fixes
            self.fixed_file, fixes_applied = self.validator.apply_auto_fixes(self.current_file)
            
            # Display fixes
            if fixes_applied:
                fixes_text = "Applied Fixes:\n\n" + "\n".join(fixes_applied)
                self.fixes_text.config(state=tk.NORMAL)
                self.fixes_text.delete(1.0, tk.END)
                self.fixes_text.insert(tk.END, fixes_text)
                self.fixes_text.config(state=tk.DISABLED)
                
                self.undo_fixes_btn.config(state=tk.NORMAL)
            else:
                self.fixes_text.config(state=tk.NORMAL)
                self.fixes_text.delete(1.0, tk.END)
                self.fixes_text.insert(tk.END, "No automatic fixes were applied.")
                self.fixes_text.config(state=tk.DISABLED)
            
            # Update validation results
            self.current_file = self.fixed_file
            self.validate_file()
            
            self.status_var.set(f"Applied {len(fixes_applied)} automatic fixes")
            
        except Exception as e:
            messagebox.showerror("Fix Error", f"Error applying fixes: {str(e)}")
            self.status_var.set("Error applying fixes")
    
    def undo_fixes(self):
        """Undo the applied fixes"""
        if not self.fixed_file:
            messagebox.showwarning("No Fixes", "No fixes to undo")
            return
        
        # Revert to original file
        self.current_file = self.validator.lars_file
        self.fixed_file = None
        
        # Clear fixes display
        self.fixes_text.config(state=tk.NORMAL)
        self.fixes_text.delete(1.0, tk.END)
        self.fixes_text.insert(tk.END, "Fixes have been undone.")
        self.fixes_text.config(state=tk.DISABLED)
        
        self.undo_fixes_btn.config(state=tk.DISABLED)
        
        # Re-display original validation results
        self.validate_file()
        
        self.status_var.set("Fixes undone")
    
    def export_file(self):
        """Export the file"""
        if not self.current_file:
            messagebox.showwarning("No File", "Please validate a file first")
            return
        
        output_path = self.output_path_var.get()
        
        if not output_path:
            messagebox.showwarning("No Output Path", "Please select an output file")
            return
        
        try:
            # Determine which file to export
            file_to_export = self.fixed_file if self.fixed_file else self.current_file
            
            # If exporting as new file and no path specified, use default
            if self.export_as_var.get() == "new" and not output_path:
                default_name = os.path.splitext(os.path.basename(self.current_file_path))[0] + "_fixed.txt"
                output_path = os.path.join(
                    os.path.dirname(self.current_file_path) or '.',
                    default_name
                )
                self.output_path_var.set(output_path)
            
            # Export the file
            success = self.validator.export_file(file_to_export, output_path)
            
            if success:
                # Update export summary
                summary = self.validator.get_summary(file_to_export)
                export_summary = f"""Export Summary
================

File: {output_path}
Version: {summary.get('version', 'Unknown')}
Total Records: {summary.get('total_records', 0)}
Valid Records: {summary.get('valid_records', 0)}
Invalid Records: {summary.get('invalid_records', 0)}
Total Errors: {summary.get('total_errors', 0)}

Export Status: SUCCESS
"""
                
                self.export_summary_text.config(state=tk.NORMAL)
                self.export_summary_text.delete(1.0, tk.END)
                self.export_summary_text.insert(tk.END, export_summary)
                self.export_summary_text.config(state=tk.DISABLED)
                
                messagebox.showinfo("Success", f"File exported successfully to:\n{output_path}")
                self.status_var.set(f"File exported to {output_path}")
            else:
                messagebox.showerror("Export Error", "Failed to export file")
                self.status_var.set("Export failed")
                
        except Exception as e:
            messagebox.showerror("Export Error", f"Error exporting file: {str(e)}")
            self.status_var.set("Export error")
    
    def clear_file(self):
        """Clear the current file"""
        self.current_file = None
        self.current_file_path = None
        self.fixed_file = None
        
        # Clear file path
        self.file_path_var.set("")
        
        # Reset buttons
        self.parse_btn.config(state=tk.DISABLED)
        self.validate_btn.config(state=tk.DISABLED)
        self.apply_fixes_btn.config(state=tk.DISABLED)
        self.undo_fixes_btn.config(state=tk.DISABLED)
        self.export_btn.config(state=tk.DISABLED)
        
        # Clear info labels
        for field in self.info_vars:
            self.info_vars[field].set("-")
        
        # Clear errors tree
        for item in self.errors_tree.get_children():
            self.errors_tree.delete(item)
        
        # Clear summary text
        self.summary_text.config(state=tk.NORMAL)
        self.summary_text.delete(1.0, tk.END)
        self.summary_text.config(state=tk.DISABLED)
        
        # Clear fixes text
        self.fixes_text.config(state=tk.NORMAL)
        self.fixes_text.delete(1.0, tk.END)
        self.fixes_text.config(state=tk.DISABLED)
        
        # Clear output path
        self.output_path_var.set("")
        
        # Clear export summary
        self.export_summary_text.config(state=tk.NORMAL)
        self.export_summary_text.delete(1.0, tk.END)
        self.export_summary_text.config(state=tk.DISABLED)
        
        # Disable tabs
        self.notebook.tab(1, state=tk.DISABLED)  # Validation tab
        self.notebook.tab(2, state=tk.DISABLED)  # Repair tab
        self.notebook.tab(3, state=tk.DISABLED)  # Export tab
        
        self.update_title()
        self.status_var.set("Ready")


def main():
    """Main entry point for the application"""
    root = tk.Tk()
    
    # Set application style
    try:
        root.tk.call('ttk', 'setTheme', 'clam')
    except:
        pass
    
    # Create and run the application
    app = LARSValidatorGUI(root)
    
    # Set window size and position
    root.geometry("1000x700")
    root.minsize(800, 500)
    
    # Center window
    root.eval('tk::PlaceWindow . center')
    
    root.mainloop()


if __name__ == "__main__":
    main()
