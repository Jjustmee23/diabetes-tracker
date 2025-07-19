#!/usr/bin/env python3
"""
Test script voor Diabetes Bloedwaarden Tracker
Controleert of alle dependencies en functionaliteiten werken
"""

import sys
import sqlite3
from datetime import datetime

def test_imports():
    """Test of alle modules correct kunnen worden geïmporteerd"""
    print("Testing imports...")
    
    try:
        import tkinter as tk
        print("✓ tkinter - OK")
    except ImportError as e:
        print(f"✗ tkinter - ERROR: {e}")
        return False
    
    try:
        import pandas as pd
        print("✓ pandas - OK")
    except ImportError as e:
        print(f"✗ pandas - ERROR: {e}")
        return False
    
    try:
        import openpyxl
        print("✓ openpyxl - OK")
    except ImportError as e:
        print(f"✗ openpyxl - ERROR: {e}")
        return False
    
    try:
        import reportlab
        print("✓ reportlab - OK")
    except ImportError as e:
        print(f"✗ reportlab - ERROR: {e}")
        return False
    
    try:
        import matplotlib
        print("✓ matplotlib - OK")
    except ImportError as e:
        print(f"✗ matplotlib - ERROR: {e}")
        return False
    
    try:
        import seaborn
        print("✓ seaborn - OK")
    except ImportError as e:
        print(f"✗ seaborn - ERROR: {e}")
        return False
    
    return True

def test_database():
    """Test database functionaliteit"""
    print("\nTesting database...")
    
    try:
        conn = sqlite3.connect('test_diabetes_data.db')
        cursor = conn.cursor()
        
        # Test tabel aanmaken
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS test_bloedwaarden (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                datum TEXT NOT NULL,
                tijd TEXT NOT NULL,
                bloedwaarde REAL NOT NULL,
                medicatie TEXT,
                activiteit TEXT,
                gewicht REAL,
                opmerkingen TEXT
            )
        ''')
        
        # Test data invoegen
        test_data = [
            ('2024-01-15', '08:30', 120.5, 'Metformine', 'Wandelen', 75.2, 'Test meting'),
            ('2024-01-15', '12:00', 95.0, 'Insuline', 'Rust', 75.1, 'Voor lunch'),
            ('2024-01-15', '18:00', 110.0, 'Metformine', 'Fietsen', 75.0, 'Na activiteit')
        ]
        
        cursor.executemany('''
            INSERT INTO test_bloedwaarden (datum, tijd, bloedwaarde, medicatie, activiteit, gewicht, opmerkingen)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', test_data)
        
        # Test data ophalen
        cursor.execute('SELECT COUNT(*) FROM test_bloedwaarden')
        count = cursor.fetchone()[0]
        
        if count == 3:
            print("✓ Database operations - OK")
            conn.close()
            return True
        else:
            print(f"✗ Database operations - ERROR: Expected 3 records, got {count}")
            conn.close()
            return False
            
    except Exception as e:
        print(f"✗ Database operations - ERROR: {e}")
        return False

def test_export_functionality():
    """Test export functionaliteit"""
    print("\nTesting export functionality...")
    
    try:
        import pandas as pd
        from datetime import datetime
        
        # Test data
        test_data = [
            ['2024-01-15', '08:30', 120.5, 'Metformine', 'Wandelen', 75.2, 'Test meting'],
            ['2024-01-15', '12:00', 95.0, 'Insuline', 'Rust', 75.1, 'Voor lunch'],
            ['2024-01-15', '18:00', 110.0, 'Metformine', 'Fietsen', 75.0, 'Na activiteit']
        ]
        
        df = pd.DataFrame(test_data, columns=[
            'Datum', 'Tijd', 'Bloedwaarde (mg/dL)', 'Medicatie', 
            'Activiteit', 'Gewicht (kg)', 'Opmerkingen'
        ])
        
        # Test Excel export
        excel_filename = 'test_export.xlsx'
        with pd.ExcelWriter(excel_filename, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='Test Data', index=False)
        
        print("✓ Excel export - OK")
        
        # Test PDF export
        try:
            from reportlab.lib.pagesizes import A4
            from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
            from reportlab.lib import colors
            
            pdf_filename = 'test_export.pdf'
            doc = SimpleDocTemplate(pdf_filename, pagesize=A4)
            
            # Convert DataFrame to list for PDF
            table_data = [df.columns.tolist()] + df.values.tolist()
            table = Table(table_data)
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 12),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            
            doc.build([table])
            print("✓ PDF export - OK")
            
        except Exception as e:
            print(f"✗ PDF export - ERROR: {e}")
            return False
        
        return True
        
    except Exception as e:
        print(f"✗ Export functionality - ERROR: {e}")
        return False

def test_chart_functionality():
    """Test grafiek functionaliteit"""
    print("\nTesting chart functionality...")
    
    try:
        import matplotlib.pyplot as plt
        import numpy as np
        
        # Test data
        dates = ['2024-01-15', '2024-01-16', '2024-01-17']
        values = [120.5, 95.0, 110.0]
        
        # Maak een eenvoudige grafiek
        plt.figure(figsize=(8, 6))
        plt.plot(dates, values, marker='o', linewidth=2)
        plt.title('Test Bloedwaarden Grafiek')
        plt.xlabel('Datum')
        plt.ylabel('Bloedwaarde (mg/dL)')
        plt.xticks(rotation=45)
        plt.tight_layout()
        
        # Sla op als test bestand
        plt.savefig('test_chart.png', dpi=150, bbox_inches='tight')
        plt.close()
        
        print("✓ Chart functionality - OK")
        return True
        
    except Exception as e:
        print(f"✗ Chart functionality - ERROR: {e}")
        return False

def cleanup_test_files():
    """Ruim test bestanden op"""
    import os
    
    test_files = [
        'test_diabetes_data.db',
        'test_export.xlsx',
        'test_export.pdf',
        'test_chart.png'
    ]
    
    for file in test_files:
        if os.path.exists(file):
            try:
                os.remove(file)
                print(f"✓ Cleaned up {file}")
            except:
                print(f"⚠ Could not clean up {file}")

def main():
    """Hoofdfunctie voor alle tests"""
    print("Diabetes Bloedwaarden Tracker - Test Script")
    print("=" * 50)
    print()
    
    all_tests_passed = True
    
    # Test imports
    if not test_imports():
        all_tests_passed = False
    
    # Test database
    if not test_database():
        all_tests_passed = False
    
    # Test export
    if not test_export_functionality():
        all_tests_passed = False
    
    # Test charts
    if not test_chart_functionality():
        all_tests_passed = False
    
    # Cleanup
    print("\nCleaning up test files...")
    cleanup_test_files()
    
    # Resultaat
    print("\n" + "=" * 50)
    if all_tests_passed:
        print("🎉 ALLE TESTS GESLAAGD!")
        print("De applicatie zou correct moeten werken.")
        print("\nJe kunt nu de applicatie starten met:")
        print("  python diabetes_tracker.py")
        print("  of dubbelklik op start_app.bat")
    else:
        print("❌ SOMIGE TESTS GEFAALD!")
        print("Controleer de foutmeldingen hierboven.")
        print("Zorg ervoor dat alle dependencies correct zijn geïnstalleerd.")
    
    print("\nDruk op Enter om af te sluiten...")
    input()

if __name__ == "__main__":
    main() 