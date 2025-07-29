#!/usr/bin/env python3
"""
Helper script untuk encode Google Service Account JSON ke base64
Untuk digunakan sebagai environment variable GOOGLE_SERVICE_ACCOUNT_KEY
"""

import json
import base64
import sys
import os
from pathlib import Path

def encode_service_account(json_file_path):
    """Encode service account JSON file to base64"""
    try:
        # Read the JSON file
        with open(json_file_path, 'r', encoding='utf-8') as f:
            json_content = f.read()
        
        # Validate JSON format
        json_data = json.loads(json_content)
        required_keys = ['type', 'project_id', 'private_key_id', 'private_key', 'client_email']
        
        for key in required_keys:
            if key not in json_data:
                print(f"❌ Error: Missing required key '{key}' in service account JSON")
                return None
        
        if json_data.get('type') != 'service_account':
            print("❌ Error: JSON file is not a service account file")
            return None
        
        # Encode to base64
        encoded = base64.b64encode(json_content.encode('utf-8')).decode('utf-8')
        
        print("✅ Service account JSON successfully encoded!")
        print(f"📧 Service Account Email: {json_data.get('client_email')}")
        print(f"🏗️ Project ID: {json_data.get('project_id')}")
        print("\n" + "="*60)
        print("📋 Copy this base64 string to your environment variable:")
        print("="*60)
        print(encoded)
        print("="*60)
        print("\n📝 Instructions:")
        print("1. Copy the base64 string above")
        print("2. Set as GOOGLE_SERVICE_ACCOUNT_KEY in:")
        print("   - Local: .env.local file")
        print("   - Vercel: Dashboard > Settings > Environment Variables")
        print("3. Make sure to share your Google Sheets with this email:")
        print(f"   {json_data.get('client_email')}")
        
        return encoded
        
    except FileNotFoundError:
        print(f"❌ Error: File '{json_file_path}' not found")
        return None
    except json.JSONDecodeError as e:
        print(f"❌ Error: Invalid JSON format: {e}")
        return None
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

def main():
    print("🔐 Google Service Account Base64 Encoder")
    print("="*50)
    
    # Check if file path provided as argument
    if len(sys.argv) > 1:
        json_file_path = sys.argv[1]
    else:
        # Interactive mode
        print("\n📁 Please provide the path to your service account JSON file:")
        print("Example: ./service-account.json")
        print("Example: C:\\path\\to\\service-account.json")
        
        json_file_path = input("\nFile path: ").strip().strip('"\'')
        
        if not json_file_path:
            print("❌ No file path provided")
            sys.exit(1)
    
    # Check if file exists
    if not os.path.exists(json_file_path):
        print(f"❌ File not found: {json_file_path}")
        
        # Suggest common locations
        print("\n💡 Looking for common service account file locations...")
        common_names = [
            "credentials.json",
            "service-account.json", 
            "service_account.json",
            "google-credentials.json"
        ]
        
        found_files = []
        for name in common_names:
            if os.path.exists(name):
                found_files.append(name)
        
        if found_files:
            print("Found these files in current directory:")
            for i, file in enumerate(found_files, 1):
                print(f"  {i}. {file}")
            
            try:
                choice = input(f"\nSelect file (1-{len(found_files)}) or Enter to exit: ").strip()
                if choice and choice.isdigit():
                    selected_idx = int(choice) - 1
                    if 0 <= selected_idx < len(found_files):
                        json_file_path = found_files[selected_idx]
                    else:
                        print("❌ Invalid selection")
                        sys.exit(1)
                else:
                    sys.exit(1)
            except (ValueError, KeyboardInterrupt):
                sys.exit(1)
        else:
            sys.exit(1)
    
    # Encode the file
    encoded = encode_service_account(json_file_path)
    
    if encoded:
        # Optionally save to file
        save_choice = input("\n💾 Save base64 string to file? (y/n): ").lower().strip()
        if save_choice == 'y':
            output_file = f"{Path(json_file_path).stem}_base64.txt"
            try:
                with open(output_file, 'w') as f:
                    f.write(encoded)
                print(f"✅ Base64 string saved to: {output_file}")
            except Exception as e:
                print(f"❌ Error saving file: {e}")

if __name__ == "__main__":
    main()
