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
        if any(term in query_normalized for term in ['used', '2nd hand', 'second hand', 'pre-owned']):
            query_normalized += ' used second-hand'
        
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
        used_trucks_df = pd.read_csv(data_path / "used_trucks.csv")
        
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
        
        for _, row in trucks_df.iterrows():
            name = str(row.get('name', '')).lower()
            capacity = str(row.get('capacity', '')).lower()
            condition = str(row.get('condition', '')).lower()
            
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
            if score > 0 or not keywords or any(word in query.lower() for word in ['truck', 'suggest', 'list', '5', 'available']):
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
        if not any(r['type'] == 'truck' for r in results) and any(word in query.lower() for word in ['truck', 'suggest', 'list', 'available']):
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
        final_results = results[:max_results]
        print(f"DEBUG: Returning {len(final_results)} results")
        return final_results
        
    except Exception as e:
        print(f"Search error: {e}")
        return []