"""
Smart knowledge filtering to prevent API exhaustion
"""
import pandas as pd
from pathlib import Path
from typing import List, Dict, Any

class KnowledgeFilter:
    def __init__(self):
        self.knowledge_df = self._load_knowledge_data()
        
    def _load_knowledge_data(self):
        """Load and clean knowledge data"""
        try:
            csv_path = Path(__file__).parent.parent.parent / "data" / "cleaned_text_content.csv"
            df = pd.read_csv(csv_path)
            
            # Remove duplicates and clean data
            df = df.drop_duplicates(subset=['title', 'text_content'])
            df = df[df['text_content'].str.len() > 100]  # Remove very short content
            
            return df
        except Exception as e:
            print(f"Error loading knowledge data: {e}")
            return pd.DataFrame()
    
    def get_relevant_content(self, user_query: str, max_entries: int = 3) -> List[Dict[str, str]]:
        """Get relevant content based on user query"""
        if self.knowledge_df.empty:
            return []
        
        query_lower = user_query.lower()
        
        # Define search priorities
        priority_keywords = {
            'contact': ['contact', 'phone', 'email', 'address', 'get in touch'],
            'trucks': ['truck', 'vehicle', 'stx', 'akx', 'ketterer', 'horse'],
            'brands': ['brand', 'model', 'stx', 'akx', 'ketterer'],
            'news': ['news', 'new', 'latest', 'announcement'],
            'ambassadors': ['ambassador', 'rider', 'champion'],
            'service': ['service', 'customer care', 'support'],
            'finance': ['finance', 'financing', 'payment', 'loan']
        }
        
        # Find matching category
        matched_category = None
        for category, keywords in priority_keywords.items():
            if any(keyword in query_lower for keyword in keywords):
                matched_category = category
                break
        
        # Filter content based on category
        if matched_category:
            filtered_df = self.knowledge_df[
                self.knowledge_df['url'].str.contains(matched_category, case=False, na=False) |
                self.knowledge_df['title'].str.contains('|'.join(priority_keywords[matched_category]), case=False, na=False)
            ]
        else:
            # General search
            filtered_df = self.knowledge_df[
                self.knowledge_df['text_content'].str.contains(query_lower, case=False, na=False)
            ]
        
        # If no specific matches, get general company info
        if filtered_df.empty:
            filtered_df = self.knowledge_df[
                self.knowledge_df['url'].str.contains('stephexhorsetrucks.com/$', regex=True, na=False)
            ].head(1)
        
        # Return limited results
        results = []
        for _, row in filtered_df.head(max_entries).iterrows():
            # Truncate content to prevent token overflow
            content = row['text_content'][:500] + "..." if len(row['text_content']) > 500 else row['text_content']
            
            results.append({
                'title': row['title'],
                'content': content,
                'url': row['url']
            })
        
        return results

# Global instance
knowledge_filter = KnowledgeFilter()