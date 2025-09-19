import pandas as pd
from pathlib import Path

def search_knowledge(query, max_results=8):
    """Smart search through comprehensive knowledge base"""
    data_path = Path(__file__).parent.parent.parent / "data"
    results = []
    keywords = query.lower().split()
    current_year = 2025
    
    try:
        # Normalize query - map synonyms
        query_normalized = query.lower()
        is_used_query = any(term in query_normalized for term in ['used', '2nd hand', 'second hand', 'pre-owned', 'second-hand'])
        if is_used_query:
            query_normalized += ' used second-hand'
            print(f"DEBUG: Detected used truck query: {query}")
        
        # Check for contact/dealer/office/company info queries first
        if any(word in query_normalized for word in ['contact', 'phone', 'email', 'address', 'office', 'location', 'where', 'dealer', 'uk', 'germany', 'france', 'netherlands', 'belgium', 'manufacture', 'built', 'vehicles', 'experience', 'employees', 'years', 'company', 'about', 'history']):
            dealer_files = ['Dealer name stx.txt', 'Dealer names AKX.txt', 'dealer names KETTERER copy.txt']
            for dealer_file in dealer_files:
                try:
                    with open(data_path / dealer_file, 'r', encoding='utf-8') as f:
                        content = f.read()
                        if 'uk' in query.lower() and 'STX-UK' in content:
                            results.append({
                                'score': 10,
                                'type': 'dealer',
                                'title': 'UK Dealer Information',
                                'content': 'STX-UK: Henfield BN5 9SL, UK - Phone: +44 1273 574 000'
                            })
                        elif any(country in content.lower() for country in keywords):
                            brand = 'STX' if 'stx' in dealer_file.lower() else ('AKX' if 'akx' in dealer_file.lower() else 'KETTERER')
                            results.append({
                                'score': 8,
                                'type': 'dealer',
                                'title': f'{brand} Dealer Network',
                                'content': content[:500]
                            })
                except:
                    pass
        # Search trucks with age filtering
        trucks_df = pd.read_csv(data_path / "trucks.csv")
        new_trucks_df = pd.read_csv(data_path / "new_trucks.csv")
        used_trucks_df = pd.read_csv(data_path / "used_trucks.csv", sep='\t')
        
        print(f"DEBUG: Loaded {len(trucks_df)} trucks from trucks.csv")
        print(f"DEBUG: Loaded {len(used_trucks_df)} trucks from used_trucks.csv with separator=tab")
        print(f"DEBUG: Used trucks columns: {list(used_trucks_df.columns)}")
        print(f"DEBUG: First row data: {used_trucks_df.iloc[0].to_dict() if len(used_trucks_df) > 0 else 'Empty'}")
        print(f"DEBUG: Is used query: {is_used_query}")
        
        # Check for age requirements
        import re
        age_requirement = None
        age_match = re.search(r'(\d+)\s*years?\s*old', query_normalized)
        if age_match:
            age_requirement = int(age_match.group(1))
        
        # Check for age-specific queries
        age_filter = None
        if ('second' in query_normalized or 'used' in query_normalized) and ('year' in query_normalized or 'old' in query_normalized):
            age_filter = 'recent_used'
        
        # If it's a used truck query, search used_trucks.csv first
        if is_used_query:
            print(f"DEBUG: Processing used trucks from used_trucks.csv")
            for _, row in used_trucks_df.iterrows():
                name = str(row.get('News__item-button-visible', '')).lower()
                print(f"DEBUG: Raw row data keys: {list(row.keys())}")
                horses = str(name).lower()  # Extract horses from name
                
                # Check if matches query (2 horses, etc.)
                score = 0
                if '2' in query and ('2' in name or 'two' in name):
                    score += 5
                score += sum(1 for word in keywords if word in name)
                
                print(f"DEBUG: Processing used truck: {name}, score: {score}, has_data: {bool(name)}")
                
                if score > 0 or not keywords or 'used' in query.lower() or 'second' in query.lower():
                    # Use actual image URLs from new CSV format
                    image_url = row.get('Image', '') or 'https://stephexhorsetrucks.com/wp-content/uploads/2021/02/STX-Trucks_donderdag_©Jeroen-Willems_WEB_127-1400x820-1-720x460.jpg'
                    detail_url = row.get('News__item URL', '') or 'https://stephexhorsetrucks.com/contact'
                    
                    # Extract capacity from truck name
                    truck_name = row.get('News__item-button-visible', '')
                    capacity = 'horses'
                    if '2 horse' in truck_name.lower() or '2-horse' in truck_name.lower():
                        capacity = '2 horses'
                    elif '4 horse' in truck_name.lower():
                        capacity = '4 horses'
                    elif '5 horse' in truck_name.lower():
                        capacity = '5 horses'
                    elif '6 horse' in truck_name.lower():
                        capacity = '6 horses'
                    elif '7 horse' in truck_name.lower():
                        capacity = '7 horses'
                    elif '8 horse' in truck_name.lower():
                        capacity = '8 horses'
                    
                    # Get detailed features and specs from used trucks Details.txt
                    features = "Second-hand truck in excellent condition"
                    year = None
                    mileage = None
                    
                    try:
                        with open(data_path / "used trucks Details.txt", 'r', encoding='utf-8') as f:
                            details_content = f.read()
                            # Find truck section in detailed file
                            truck_section_start = details_content.find(truck_name)
                            if truck_section_start != -1:
                                # Get section from truck name to next truck or end
                                next_truck = details_content.find('Brand:', truck_section_start + len(truck_name))
                                if next_truck != -1:
                                    next_next_truck = details_content.find('Brand:', next_truck + 10)
                                    truck_section = details_content[truck_section_start:next_next_truck if next_next_truck != -1 else truck_section_start + 2000]
                                else:
                                    truck_section = details_content[truck_section_start:truck_section_start + 2000]
                                
                                # Extract year and mileage
                                if 'Year:' in truck_section:
                                    year_match = truck_section[truck_section.find('Year:'):truck_section.find('Year:') + 20]
                                    try:
                                        year = int(''.join(filter(str.isdigit, year_match)))
                                    except:
                                        pass
                                
                                if 'Mileage:' in truck_section:
                                    mileage_match = truck_section[truck_section.find('Mileage:'):truck_section.find('Mileage:') + 30]
                                    mileage = mileage_match.replace('Mileage:', '').strip().split()[0] if 'km' in mileage_match else None
                                
                                # Extract features
                                if 'Features' in truck_section:
                                    features_start = truck_section.find('Features')
                                    features_end = truck_section.find('GET YOUR OFFER', features_start)
                                    if features_end == -1:
                                        features_end = features_start + 800
                                    features_text = truck_section[features_start:features_end].replace('Features', '').strip()
                                    if len(features_text) > 50:
                                        features = features_text[:600]
                    except:
                        pass
                    
                    results.append({
                        'score': score + 10,  # Higher score for used trucks
                        'type': 'truck',
                        'title': truck_name,
                        'capacity': capacity,
                        'condition': 'Used',
                        'year': year,
                        'mileage': mileage,
                        'features': features,
                        'image_url': image_url,
                        'url': detail_url
                    })
        
        # Search main trucks.csv
        for _, row in trucks_df.iterrows():
            name = str(row.get('name', '')).lower()
            capacity = str(row.get('capacity', '')).lower()
            condition = str(row.get('condition', '')).lower()
            
            # Skip if used query but this is new truck
            if is_used_query and condition not in ['used', 'second-hand']:
                continue
            
            # Get year from detailed data
            truck_year = None
            for _, detail_row in used_trucks_df.iterrows():
                if str(detail_row.get('Name', '')).lower() in name:
                    truck_year = detail_row.get('Year')
                    break
            if not truck_year:
                for _, detail_row in new_trucks_df.iterrows():
                    if str(detail_row.get('Name', '')).lower() in name:
                        truck_year = detail_row.get('Year')
                        break
            
            # Apply age filter
            if age_requirement and truck_year:
                truck_age = current_year - int(truck_year)
                if truck_age > age_requirement:
                    continue
            
            # Apply used truck filter
            if age_filter == 'recent_used':
                if condition in ['used', 'second-hand']:
                    if truck_year and int(truck_year) >= 2023:
                        pass
                    else:
                        continue
                else:
                    continue
            
            score = sum(1 for word in keywords if word in name or word in capacity)
            # Always show trucks for general queries
            if score > 0 or not keywords or any(word in query.lower() for word in ['truck', 'suggest', 'list', '5', 'available', 'used', 'second']):
                # Find detailed features
                features = ""
                for _, detail_row in new_trucks_df.iterrows():
                    if str(detail_row.get('Name', '')).lower() in name:
                        features = str(detail_row.get('Features', ''))[:300]
                        break
                
                results.append({
                    'score': score + 3,
                    'type': 'truck',
                    'title': row.get('name', ''),
                    'capacity': row.get('capacity', ''),
                    'condition': row.get('condition', ''),
                    'year': truck_year,
                    'features': features,
                    'image_url': row.get('image_url', ''),
                    'url': row.get('url', '')
                })
        
        # If no trucks found, search new_trucks.csv as backup
        if not any(r['type'] == 'truck' for r in results):
            new_df = pd.read_csv(data_path / "new_trucks.csv")
            for _, row in new_df.iterrows():
                name = str(row.get('Name', '')).lower()
                score = sum(1 for word in keywords if word in name)
                if score > 0 or not keywords:
                    results.append({
                        'score': score + 2,
                        'type': 'new_truck',
                        'title': row.get('Name', ''),
                        'content': f"{row.get('Horses', '')} horses | {row.get('Year', '')}"
                    })
        

        
        # Search contact info - prioritize for contact/office/company queries
        if any(word in query_normalized for word in ['contact', 'phone', 'email', 'address', 'info', 'office', 'location', 'where', 'manufacture', 'built', 'vehicles', 'experience', 'employees', 'years', 'company', 'about', 'history']):
            with open(data_path / "contact.txt", 'r', encoding='utf-8') as f:
                contact_content = f.read()
                results.append({
                    'score': 100,  # High priority for company info queries
                    'type': 'contact',
                    'title': 'Company Information',
                    'content': contact_content
                })
        else:
            # Regular contact search for other queries
            with open(data_path / "contact.txt", 'r', encoding='utf-8') as f:
                contact_text = f.read().lower()
                score = sum(1 for word in keywords if word in contact_text)
                if score > 0:
                    results.append({
                        'score': score,
                        'type': 'contact',
                        'title': 'Contact Information',
                        'content': contact_text
                    })
        
        # Ensure we have trucks for general queries
        if not any(r['type'] == 'truck' for r in results) and any(word in query.lower() for word in ['truck', 'suggest', 'list', 'available', 'used', 'second']):
            # Force load all trucks
            for _, row in trucks_df.iterrows():
                results.append({
                    'score': 1,
                    'type': 'truck',
                    'title': row.get('name', ''),
                    'capacity': row.get('capacity', ''),
                    'condition': row.get('condition', ''),
                    'year': None,
                    'features': '',
                    'image_url': row.get('image_url', ''),
                    'url': row.get('url', '')
                })
        
        results.sort(key=lambda x: x['score'], reverse=True)
        print(f"DEBUG: Total results before limit: {len(results)}")
        print(f"DEBUG: Truck results: {[r['title'] for r in results if r['type'] == 'truck']}")
        print(f"DEBUG: Used truck count: {len([r for r in results if r['type'] == 'truck' and r.get('condition') == 'Used'])}")
        final_results = results[:max_results]
        print(f"DEBUG: Returning {len(final_results)} results")
        return final_results
        
    except Exception as e:
        print(f"Search error: {e}")
        return []