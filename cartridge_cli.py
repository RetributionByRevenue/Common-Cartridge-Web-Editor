#!/usr/bin/env python3
"""
Command Line Interface for Canvas Common Cartridge Generator
"""

import argparse
import sys
from pathlib import Path
import shutil
from cartridge_engine import CartridgeGenerator


def create_cartridge(args):
    """Create a new cartridge"""
    cartridge_path = Path(args.cartridge_name)
    
    if cartridge_path.exists():
        print(f"Error: Directory '{args.cartridge_name}' already exists")
        return 1
    
    # Create generator
    generator = CartridgeGenerator(args.title, args.code)
    
    # Create base cartridge
    print(f"Creating cartridge: {args.cartridge_name}")
    generator.create_base_cartridge(args.cartridge_name)
    
    print(f"✓ Cartridge '{args.cartridge_name}' created successfully")
    print(f"  Title: {args.title}")
    print(f"  Code: {args.code}")
    print(f"  Components: {len(generator.df)}")
    
    return 0


def add_module(args):
    """Add a module to an existing cartridge"""
    cartridge_path = Path(args.cartridge_name)
    
    if not cartridge_path.exists():
        print(f"Error: Cartridge '{args.cartridge_name}' does not exist")
        return 1
    
    # Load existing cartridge
    generator = CartridgeGenerator("temp", "temp", verbose=False)  # Will be overridden during hydration
    if not generator.hydrate_from_existing_cartridge(args.cartridge_name):
        print("Failed to load existing cartridge")
        return 1
    
    # Add module
    print(f"Adding module '{args.title}' to cartridge '{args.cartridge_name}'")
    module_id = generator.add_module(args.title, position=args.position, published=args.published)
    
    print(f"✓ Module '{args.title}' added successfully")
    print(f"  Module ID: {module_id}")
    print(f"  Position: {args.position}")
    print(f"  Published: {args.published}")
    print(f"  Total components: {len(generator.df)}")
    
    return 0


def add_wiki(args):
    """Add a wiki page to a module in an existing cartridge"""
    cartridge_path = Path(args.cartridge_name)
    
    if not cartridge_path.exists():
        print(f"Error: Cartridge '{args.cartridge_name}' does not exist")
        return 1
    
    # Load existing cartridge
    generator = CartridgeGenerator("temp", "temp", verbose=False)  # Will be overridden during hydration
    if not generator.hydrate_from_existing_cartridge(args.cartridge_name):
        print("Failed to load existing cartridge")
        return 1
    
    # Find module by title
    try:
        module_row = generator.df[(generator.df["type"] == "module") & (generator.df["title"] == args.module)]
        if module_row.empty:
            print(f"Error: Module '{args.module}' not found in cartridge")
            print("Available modules:")
            modules = generator.df[generator.df["type"] == "module"]["title"].tolist()
            for module in modules:
                print(f"  - {module}")
            return 1
        
        module_id = module_row.iloc[0]["identifier"]
        
    except Exception as e:
        print(f"Error finding module: {e}")
        return 1
    
    # Add wiki page to module
    print(f"Adding wiki page '{args.title}' to module '{args.module}' in cartridge '{args.cartridge_name}'")
    generator.add_wiki_page_to_module(module_id, args.title, page_content=args.content, published=True, position=None)
    
    print(f"✓ Wiki page '{args.title}' added successfully")
    print(f"  Module: {args.module}")
    print(f"  Content length: {len(args.content)} characters")
    print(f"  Total components: {len(generator.df)}")
    
    return 0


def add_assignment(args):
    """Add an assignment to a module in an existing cartridge"""
    cartridge_path = Path(args.cartridge_name)
    
    if not cartridge_path.exists():
        print(f"Error: Cartridge '{args.cartridge_name}' does not exist")
        return 1
    
    # Load existing cartridge
    generator = CartridgeGenerator("temp", "temp", verbose=False)  # Will be overridden during hydration
    if not generator.hydrate_from_existing_cartridge(args.cartridge_name):
        print("Failed to load existing cartridge")
        return 1
    
    # Find module by title
    try:
        module_row = generator.df[(generator.df["type"] == "module") & (generator.df["title"] == args.module)]
        if module_row.empty:
            print(f"Error: Module '{args.module}' not found in cartridge")
            print("Available modules:")
            modules = generator.df[generator.df["type"] == "module"]["title"].tolist()
            for module in modules:
                print(f"  - {module}")
            return 1
        
        module_id = module_row.iloc[0]["identifier"]
        
    except Exception as e:
        print(f"Error finding module: {e}")
        return 1
    
    # Add assignment to module
    print(f"Adding assignment '{args.title}' to module '{args.module}' in cartridge '{args.cartridge_name}'")
    generator.add_assignment_to_module(module_id, args.title, assignment_content=args.content, points=args.points, published=True, position=None)
    
    print(f"✓ Assignment '{args.title}' added successfully")
    print(f"  Module: {args.module}")
    print(f"  Points: {args.points}")
    print(f"  Content length: {len(args.content)} characters")
    print(f"  Total components: {len(generator.df)}")
    
    return 0


def add_quiz(args):
    """Add a quiz to a module in an existing cartridge"""
    cartridge_path = Path(args.cartridge_name)
    
    if not cartridge_path.exists():
        print(f"Error: Cartridge '{args.cartridge_name}' does not exist")
        return 1
    
    # Load existing cartridge
    generator = CartridgeGenerator("temp", "temp", verbose=False)  # Will be overridden during hydration
    if not generator.hydrate_from_existing_cartridge(args.cartridge_name):
        print("Failed to load existing cartridge")
        return 1
    
    # Find module by title
    try:
        module_row = generator.df[(generator.df["type"] == "module") & (generator.df["title"] == args.module)]
        if module_row.empty:
            print(f"Error: Module '{args.module}' not found in cartridge")
            print("Available modules:")
            modules = generator.df[generator.df["type"] == "module"]["title"].tolist()
            for module in modules:
                print(f"  - {module}")
            return 1
        
        module_id = module_row.iloc[0]["identifier"]
        
    except Exception as e:
        print(f"Error finding module: {e}")
        return 1
    
    # Add quiz to module
    print(f"Adding quiz '{args.title}' to module '{args.module}' in cartridge '{args.cartridge_name}'")
    generator.add_quiz_to_module(module_id, args.title, quiz_description=args.description, points=args.points, published=True, position=None)
    
    print(f"✓ Quiz '{args.title}' added successfully")
    print(f"  Module: {args.module}")
    print(f"  Points: {args.points}")
    print(f"  Description length: {len(args.description)} characters")
    print(f"  Total components: {len(generator.df)}")
    
    return 0


def add_discussion(args):
    """Add a discussion to a module in an existing cartridge"""
    cartridge_path = Path(args.cartridge_name)
    
    if not cartridge_path.exists():
        print(f"Error: Cartridge '{args.cartridge_name}' does not exist")
        return 1
    
    # Load existing cartridge
    generator = CartridgeGenerator("temp", "temp", verbose=False)  # Will be overridden during hydration
    if not generator.hydrate_from_existing_cartridge(args.cartridge_name):
        print("Failed to load existing cartridge")
        return 1
    
    # Find module by title
    try:
        module_row = generator.df[(generator.df["type"] == "module") & (generator.df["title"] == args.module)]
        if module_row.empty:
            print(f"Error: Module '{args.module}' not found in cartridge")
            print("Available modules:")
            modules = generator.df[generator.df["type"] == "module"]["title"].tolist()
            for module in modules:
                print(f"  - {module}")
            return 1
        
        module_id = module_row.iloc[0]["identifier"]
        
    except Exception as e:
        print(f"Error finding module: {e}")
        return 1
    
    # Add discussion to module
    print(f"Adding discussion '{args.title}' to module '{args.module}' in cartridge '{args.cartridge_name}'")
    generator.add_discussion_to_module(module_id, args.title, args.description, published=True, position=None)
    
    print(f"✓ Discussion '{args.title}' added successfully")
    print(f"  Module: {args.module}")
    print(f"  Description length: {len(args.description)} characters")
    print(f"  Total components: {len(generator.df)}")
    
    return 0


def add_file(args):
    """Add a file to a module in an existing cartridge"""
    cartridge_path = Path(args.cartridge_name)
    
    if not cartridge_path.exists():
        print(f"Error: Cartridge '{args.cartridge_name}' does not exist")
        return 1
    
    # Load existing cartridge
    generator = CartridgeGenerator("temp", "temp", verbose=False)  # Will be overridden during hydration
    if not generator.hydrate_from_existing_cartridge(args.cartridge_name):
        print("Failed to load existing cartridge")
        return 1
    
    # Find module by title
    try:
        module_row = generator.df[(generator.df["type"] == "module") & (generator.df["title"] == args.module)]
        if module_row.empty:
            print(f"Error: Module '{args.module}' not found in cartridge")
            print("Available modules:")
            modules = generator.df[generator.df["type"] == "module"]["title"].tolist()
            for module in modules:
                print(f"  - {module}")
            return 1
        
        module_id = module_row.iloc[0]["identifier"]
        
    except Exception as e:
        print(f"Error finding module: {e}")
        return 1
    
    # Add file to module
    print(f"Adding file '{args.filename}' to module '{args.module}' in cartridge '{args.cartridge_name}'")
    generator.add_file_to_module(module_id, args.filename, args.content, position=None)
    
    print(f"✓ File '{args.filename}' added successfully")
    print(f"  Module: {args.module}")
    print(f"  Content length: {len(args.content)} characters")
    print(f"  Total components: {len(generator.df)}")
    
    return 0


def list_cartridge(args):
    """List contents of an existing cartridge"""
    import json
    import xml.etree.ElementTree as ET
    
    cartridge_path = Path(args.cartridge_name)
    
    if not cartridge_path.exists():
        if hasattr(args, 'json') and args.json:
            print(json.dumps({"error": f"Cartridge '{args.cartridge_name}' does not exist"}))
        else:
            print(f"Error: Cartridge '{args.cartridge_name}' does not exist")
        return 1
    
    # Load existing cartridge
    generator = CartridgeGenerator("temp", "temp", verbose=False)  # Will be overridden during hydration
    if not generator.hydrate_from_existing_cartridge(args.cartridge_name):
        if hasattr(args, 'json') and args.json:
            print(json.dumps({"error": "Failed to load existing cartridge"}))
        else:
            print("Failed to load existing cartridge")
        return 1
    
    # Get summary
    summary = generator.get_hydration_summary()
    
    # Build module structure for both JSON and text output
    modules_data = []
    modules = generator.df[generator.df["type"] == "module"]
    
    if not modules.empty:
        # Parse organization structure from manifest to get proper module-item hierarchy
        manifest_row = generator.df[generator.df["type"] == "manifest"]
        if not manifest_row.empty:
            try:
                manifest_xml = manifest_row.iloc[0]['xml_content']
                root = ET.fromstring(manifest_xml)
                
                # Find LearningModules organization
                learning_modules = root.find('.//{http://www.imsglobal.org/xsd/imsccv1p1/imscp_v1p1}item[@identifier="LearningModules"]')
                if learning_modules is not None:
                    # Create a mapping of module ID to its items
                    module_items_map = {}
                    
                    for module_item in learning_modules.findall('.//{http://www.imsglobal.org/xsd/imsccv1p1/imscp_v1p1}item'):
                        if module_item.get('identifier') != 'LearningModules':
                            module_id = module_item.get('identifier')
                            title_elem = module_item.find('.//{http://www.imsglobal.org/xsd/imsccv1p1/imscp_v1p1}title')
                            
                            # Find child items of this module
                            child_items = []
                            for child in module_item.findall('.//{http://www.imsglobal.org/xsd/imsccv1p1/imscp_v1p1}item'):
                                if child != module_item:  # Exclude the module itself
                                    child_title_elem = child.find('.//{http://www.imsglobal.org/xsd/imsccv1p1/imscp_v1p1}title')
                                    child_title = child_title_elem.text if child_title_elem is not None else None
                                    child_ref = child.get('identifierref')
                                    if child_title:
                                        child_items.append({
                                            'title': child_title,
                                            'identifierref': child_ref
                                        })
                            
                            module_items_map[module_id] = child_items
                    
                    # Build modules data structure
                    for _, module in modules.iterrows():
                        module_items = module_items_map.get(module['identifier'], [])
                        
                        # Remove duplicates while preserving order
                        seen_items = set()
                        unique_items = []
                        for item in module_items:
                            item_key = item['title'] if isinstance(item, dict) else item
                            if item_key not in seen_items:
                                seen_items.add(item_key)
                                unique_items.append(item)
                        
                        # Process items and determine content types
                        items_data = []
                        for item in unique_items:
                            if isinstance(item, dict):
                                item_title = item['title']
                                identifierref = item.get('identifierref')
                                
                                # Look up content type from resource or module_item data
                                content_type = "WikiPage"  # Default
                                
                                # Try to determine content type from identifierref
                                if identifierref:
                                    # Check resources for this identifierref
                                    resource_match = generator.df[
                                        (generator.df['identifier'] == identifierref) & 
                                        (generator.df['type'] == 'resource')
                                    ]
                                    if not resource_match.empty:
                                        resource_type = resource_match.iloc[0]['resource_type']
                                        if resource_type:
                                            if 'assessment' in resource_type:
                                                content_type = "Quiz"
                                            elif 'imsdt' in resource_type:
                                                content_type = "Discussion"
                                            elif resource_type == 'webcontent':
                                                content_type = "WikiPage"
                                            elif 'assignment' in resource_type:
                                                content_type = "Assignment"
                                            else:
                                                content_type = "File"
                                
                                # Also check module_item data for content_type
                                module_item_match = generator.df[
                                    (generator.df['title'] == item_title) & 
                                    (generator.df['type'] == 'module_item')
                                ]
                                if not module_item_match.empty:
                                    item_content_type = module_item_match.iloc[0].get('content_type')
                                    if item_content_type:
                                        content_type = item_content_type
                                        # Clean up content type names
                                        if content_type == "Quizzes::Quiz":
                                            content_type = "Quiz"
                                        elif content_type == "Attachment":
                                            content_type = "File"
                                
                                items_data.append({
                                    'title': item_title,
                                    'identifierref': identifierref,
                                    'content_type': content_type
                                })
                            else:
                                # Fallback for old format
                                items_data.append({
                                    'title': item,
                                    'identifierref': None,
                                    'content_type': "WikiPage"
                                })
                        
                        modules_data.append({
                            'id': module['identifier'],
                            'title': module['title'],
                            'items': items_data
                        })
                            
            except ET.ParseError as e:
                # Fallback to simple module listing
                for _, module in modules.iterrows():
                    modules_data.append({
                        'id': module['identifier'],
                        'title': module['title'],
                        'items': []
                    })
    
    # Output based on format requested
    if hasattr(args, 'json') and args.json:
        # JSON output only
        output_data = {
            'cartridge_name': args.cartridge_name,
            'course_title': summary['course_title'],
            'course_code': summary['course_code'],
            'total_components': summary['total_components'],
            'modules': modules_data,
            'component_types': {k: int(v) for k, v in summary['component_types'].items()}
        }
        print(json.dumps(output_data, indent=2))
    else:
        # Text output (original format)
        print(f"Cartridge: {args.cartridge_name}")
        print(f"  Course: {summary['course_title']} ({summary['course_code']})")
        print(f"  Total components: {summary['total_components']}")
        print()
        
        if modules_data:
            print("Modules:")
            for module in modules_data:
                print(f"  📁 {module['title']} (ID: {module['id']})")
                
                if module['items']:
                    for item in module['items']:
                        icons = {
                            "WikiPage": "📄",
                            "Assignment": "📝", 
                            "Quiz": "❓",
                            "DiscussionTopic": "💬",
                            "Discussion": "💬",
                            "File": "📎"
                        }
                        icon = icons.get(item['content_type'], "❓")
                        print(f"    {icon} {item['title']} ({item['content_type']})")
                else:
                    print("    (no items)")
        
        # List component types
        print("\nComponent breakdown:")
        for comp_type, count in summary['component_types'].items():
            print(f"  {comp_type}: {count}")
        
        # Export DataFrame to HTML for inspection
        html_file = f"{args.cartridge_name}/table_inspect.html"
        temp_display_df = generator.current_df.copy()
        for index, row in temp_display_df.iterrows():
            if len(str(row['xml_content'])) > 2000:
                temp_display_df.at[index, 'xml_content'] = str(row['xml_content'])[:2000] + " ... cell length reached limit"
        temp_display_df.to_html(html_file, escape=False)
        print(f"\n✓ DataFrame exported to {html_file} for inspection")
    
    return 0


def update_wiki(args):
    """Update a wiki page in an existing cartridge"""
    cartridge_path = Path(args.cartridge_name)
    
    if not cartridge_path.exists():
        print(f"Error: Cartridge '{args.cartridge_name}' does not exist")
        return 1
    
    # Load existing cartridge
    generator = CartridgeGenerator("temp", "temp", verbose=False)  # Will be overridden during hydration
    if not generator.hydrate_from_existing_cartridge(args.cartridge_name):
        print("Failed to load existing cartridge")
        return 1
    
    # Find wiki page by title
    try:
        wiki_pages = generator.df[(generator.df["type"] == "wiki_page") & (generator.df["title"] == args.title)]
        if wiki_pages.empty:
            print(f"Error: Wiki page '{args.title}' not found in cartridge")
            print("Available wiki pages:")
            all_wiki_pages = generator.df[generator.df["type"] == "wiki_page"]["title"].tolist()
            if all_wiki_pages:
                for page in all_wiki_pages:
                    print(f"  - {page}")
            else:
                print("  (no wiki pages found)")
            return 1
        
        wiki_page_id = wiki_pages.iloc[0]["identifier"]
        
    except Exception as e:
        print(f"Error finding wiki page: {e}")
        return 1
    
    # Update wiki page
    try:
        print(f"Updating wiki page '{args.title}' in cartridge '{args.cartridge_name}'")
        generator.update_wiki(
            wiki_page_id, 
            page_title=args.new_title,
            page_content=args.content,
            published=args.published,
            position=args.position
        )
        
        print(f"  Total components: {len(generator.df)}")
        
    except Exception as e:
        print(f"Error updating wiki page: {e}")
        return 1
    
    return 0


def copy_wiki(args):
    """Copy a wiki page to another module in an existing cartridge"""
    cartridge_path = Path(args.cartridge_name)
    
    if not cartridge_path.exists():
        print(f"Error: Cartridge '{args.cartridge_name}' does not exist")
        return 1
    
    # Load existing cartridge
    generator = CartridgeGenerator("temp", "temp", verbose=False)  # Will be overridden during hydration
    if not generator.hydrate_from_existing_cartridge(args.cartridge_name):
        print("Failed to load existing cartridge")
        return 1
    
    # Find wiki page by title
    try:
        wiki_pages = generator.df[(generator.df["type"] == "wiki_page") & (generator.df["title"] == args.title)]
        if wiki_pages.empty:
            print(f"Error: Wiki page '{args.title}' not found in cartridge")
            print("Available wiki pages:")
            all_wiki_pages = generator.df[generator.df["type"] == "wiki_page"]["title"].tolist()
            if all_wiki_pages:
                for page in all_wiki_pages:
                    print(f"  - {page}")
            else:
                print("  (no wiki pages found)")
            return 1
        
        selected_wiki = wiki_pages.iloc[0]["identifier"]
        
    except Exception as e:
        print(f"Error finding wiki page: {e}")
        return 1
    
    # Find target module by title
    try:
        target_module_row = generator.df[(generator.df["type"] == "module") & (generator.df["title"] == args.target_module)]
        if target_module_row.empty:
            print(f"Error: Target module '{args.target_module}' not found in cartridge")
            print("Available modules:")
            modules = generator.df[generator.df["type"] == "module"]["title"].tolist()
            for module in modules:
                print(f"  - {module}")
            return 1
        
        target_module_id = target_module_row.iloc[0]["identifier"]
        
    except Exception as e:
        print(f"Error finding target module: {e}")
        return 1
    
    # Copy wiki page to target module
    try:
        print(f"Copying wiki page '{args.title}' to module '{args.target_module}' in cartridge '{args.cartridge_name}'")
        new_wiki_id = generator.copy_wiki_page(selected_wiki, target_module_id)
        
        print(f"✓ Wiki page '{args.title}' copied successfully")
        print(f"  New wiki ID: {new_wiki_id}")
        print(f"  Target module: {args.target_module}")
        print(f"  Total components: {len(generator.df)}")
        
    except Exception as e:
        print(f"Error copying wiki page: {e}")
        return 1
    
    return 0


def copy_assignment(args):
    """Copy an assignment to another module in an existing cartridge"""
    cartridge_path = Path(args.cartridge_name)
    
    if not cartridge_path.exists():
        print(f"Error: Cartridge '{args.cartridge_name}' does not exist")
        return 1
    
    # Load existing cartridge
    generator = CartridgeGenerator("temp", "temp", verbose=False)  # Will be overridden during hydration
    if not generator.hydrate_from_existing_cartridge(args.cartridge_name):
        print("Failed to load existing cartridge")
        return 1
    
    # Find assignment by title
    try:
        assignments = generator.df[(generator.df["type"] == "assignment_settings") & (generator.df["title"] == args.title)]
        if assignments.empty:
            print(f"Error: Assignment '{args.title}' not found in cartridge")
            print("Available assignments:")
            all_assignments = generator.df[generator.df["type"] == "assignment_settings"]["title"].tolist()
            if all_assignments:
                for assignment in all_assignments:
                    print(f"  - {assignment}")
            else:
                print("  (no assignments found)")
            return 1
        
        selected_assignment = assignments.iloc[0]["identifier"]
        
    except Exception as e:
        print(f"Error finding assignment: {e}")
        return 1
    
    # Find target module by title
    try:
        target_module_row = generator.df[(generator.df["type"] == "module") & (generator.df["title"] == args.target_module)]
        if target_module_row.empty:
            print(f"Error: Target module '{args.target_module}' not found in cartridge")
            print("Available modules:")
            modules = generator.df[generator.df["type"] == "module"]["title"].tolist()
            for module in modules:
                print(f"  - {module}")
            return 1
        
        target_module_id = target_module_row.iloc[0]["identifier"]
        
    except Exception as e:
        print(f"Error finding target module: {e}")
        return 1
    
    # Copy assignment to target module
    try:
        print(f"Copying assignment '{args.title}' to module '{args.target_module}' in cartridge '{args.cartridge_name}'")
        new_assignment_id = generator.copy_assignment(selected_assignment, target_module_id)
        
        print(f"✓ Assignment '{args.title}' copied successfully")
        print(f"  New assignment ID: {new_assignment_id}")
        print(f"  Target module: {args.target_module}")
        print(f"  Total components: {len(generator.df)}")
        
    except Exception as e:
        print(f"Error copying assignment: {e}")
        return 1
    
    return 0


def copy_discussion(args):
    """Copy a discussion to another module in an existing cartridge"""
    cartridge_path = Path(args.cartridge_name)
    
    if not cartridge_path.exists():
        print(f"Error: Cartridge '{args.cartridge_name}' does not exist")
        return 1
    
    # Load existing cartridge
    generator = CartridgeGenerator("temp", "temp", verbose=False)  # Will be overridden during hydration
    if not generator.hydrate_from_existing_cartridge(args.cartridge_name):
        print("Failed to load existing cartridge")
        return 1
    
    # Find discussion by title - discussions use module items with Discussion content type
    try:
        discussion_items = generator.df[
            (generator.df["type"] == "module_item") & 
            (generator.df["title"] == args.title) &
            (generator.df["content_type"].isin(["DiscussionTopic", "Discussion"]))
        ]
        
        if discussion_items.empty:
            print(f"Error: Discussion '{args.title}' not found in cartridge")
            print("Available discussions:")
            all_discussions = generator.df[
                (generator.df["type"] == "module_item") & 
                (generator.df["content_type"].isin(["DiscussionTopic", "Discussion"]))
            ]["title"].tolist()
            if all_discussions:
                for discussion in all_discussions:
                    print(f"  - {discussion}")
            else:
                print("  (no discussions found)")
            return 1
        
        # Get the identifierref from the module item to find the actual discussion resource
        discussion_item = discussion_items.iloc[0]
        selected_discussion = discussion_item["identifierref"]
        
    except Exception as e:
        print(f"Error finding discussion: {e}")
        return 1
    
    # Find target module by title
    try:
        target_module_row = generator.df[(generator.df["type"] == "module") & (generator.df["title"] == args.target_module)]
        if target_module_row.empty:
            print(f"Error: Target module '{args.target_module}' not found in cartridge")
            print("Available modules:")
            modules = generator.df[generator.df["type"] == "module"]["title"].tolist()
            for module in modules:
                print(f"  - {module}")
            return 1
        
        target_module_id = target_module_row.iloc[0]["identifier"]
        
    except Exception as e:
        print(f"Error finding target module: {e}")
        return 1
    
    # Copy discussion to target module
    try:
        print(f"Copying discussion '{args.title}' to module '{args.target_module}' in cartridge '{args.cartridge_name}'")
        new_discussion_id = generator.copy_discussion(selected_discussion, target_module_id)
        
        print(f"✓ Discussion '{args.title}' copied successfully")
        print(f"  New discussion ID: {new_discussion_id}")
        print(f"  Target module: {args.target_module}")
        print(f"  Total components: {len(generator.df)}")
        
    except Exception as e:
        print(f"Error copying discussion: {e}")
        return 1
    
    return 0


def copy_quiz(args):
    """Copy a quiz to another module in an existing cartridge"""
    cartridge_path = Path(args.cartridge_name)
    
    if not cartridge_path.exists():
        print(f"Error: Cartridge '{args.cartridge_name}' does not exist")
        return 1
    
    # Load existing cartridge
    generator = CartridgeGenerator("temp", "temp", verbose=False)  # Will be overridden during hydration
    if not generator.hydrate_from_existing_cartridge(args.cartridge_name):
        print("Failed to load existing cartridge")
        return 1
    
    # Find quiz by title - quizzes use type "assessment_meta"
    try:
        quiz_assessments = generator.df[
            (generator.df["type"] == "assessment_meta") & 
            (generator.df["title"] == args.title)
        ]
        
        if quiz_assessments.empty:
            print(f"Error: Quiz '{args.title}' not found in cartridge")
            print("Available quizzes:")
            all_quizzes = generator.df[
                generator.df["type"] == "assessment_meta"
            ]["title"].tolist()
            if all_quizzes:
                for quiz in all_quizzes:
                    print(f"  - {quiz}")
            else:
                print("  (no quizzes found)")
            return 1
        
        selected_quiz = quiz_assessments.iloc[0]["identifier"]
        
    except Exception as e:
        print(f"Error finding quiz: {e}")
        return 1
    
    # Find target module by title
    try:
        target_module_row = generator.df[(generator.df["type"] == "module") & (generator.df["title"] == args.target_module)]
        if target_module_row.empty:
            print(f"Error: Target module '{args.target_module}' not found in cartridge")
            print("Available modules:")
            modules = generator.df[generator.df["type"] == "module"]["title"].tolist()
            for module in modules:
                print(f"  - {module}")
            return 1
        
        target_module_id = target_module_row.iloc[0]["identifier"]
        
    except Exception as e:
        print(f"Error finding target module: {e}")
        return 1
    
    # Copy quiz to target module
    try:
        print(f"Copying quiz '{args.title}' to module '{args.target_module}' in cartridge '{args.cartridge_name}'")
        new_quiz_id = generator.copy_quiz(selected_quiz, target_module_id)
        
        print(f"✓ Quiz '{args.title}' copied successfully")
        print(f"  New quiz ID: {new_quiz_id}")
        print(f"  Target module: {args.target_module}")
        print(f"  Total components: {len(generator.df)}")
        
    except Exception as e:
        print(f"Error copying quiz: {e}")
        return 1
    
    return 0


def copy_file(args):
    """Copy a file to another module in an existing cartridge"""
    cartridge_path = Path(args.cartridge_name)
    
    if not cartridge_path.exists():
        print(f"Error: Cartridge '{args.cartridge_name}' does not exist")
        return 1
    
    # Load existing cartridge
    generator = CartridgeGenerator("temp", "temp", verbose=False)  # Will be overridden during hydration
    if not generator.hydrate_from_existing_cartridge(args.cartridge_name):
        print("Failed to load existing cartridge")
        return 1
    
    # Find file by filename - files use type "resource" and href contains web_resources/filename
    try:
        file_resources = generator.df[
            (generator.df["type"] == "resource") & 
            (generator.df["href"].str.contains(f"web_resources/{args.filename}", na=False))
        ]
        
        if file_resources.empty:
            print(f"Error: File '{args.filename}' not found in cartridge")
            print("Available files:")
            all_files = generator.df[
                (generator.df["type"] == "resource") & 
                (generator.df["href"].str.contains("web_resources/", na=False))
            ]["href"].tolist()
            if all_files:
                for file_href in all_files:
                    filename = file_href.split("/")[-1] if "/" in file_href else file_href
                    print(f"  - {filename}")
            else:
                print("  (no files found)")
            return 1
        
        selected_file = file_resources.iloc[0]["identifier"]
        
    except Exception as e:
        print(f"Error finding file: {e}")
        return 1
    
    # Find target module by title
    try:
        target_module_row = generator.df[(generator.df["type"] == "module") & (generator.df["title"] == args.target_module)]
        if target_module_row.empty:
            print(f"Error: Target module '{args.target_module}' not found in cartridge")
            print("Available modules:")
            modules = generator.df[generator.df["type"] == "module"]["title"].tolist()
            for module in modules:
                print(f"  - {module}")
            return 1
        
        target_module_id = target_module_row.iloc[0]["identifier"]
        
    except Exception as e:
        print(f"Error finding target module: {e}")
        return 1
    
    # Copy file to target module
    try:
        print(f"Copying file '{args.filename}' to module '{args.target_module}' in cartridge '{args.cartridge_name}'")
        new_file_id = generator.copy_file(selected_file, target_module_id)
        
        print(f"✓ File '{args.filename}' copied successfully")
        print(f"  New file ID: {new_file_id}")
        print(f"  Target module: {args.target_module}")
        print(f"  Total components: {len(generator.df)}")
        
    except Exception as e:
        print(f"Error copying file: {e}")
        return 1
    
    return 0


def update_assignment(args):
    """Update an assignment in an existing cartridge"""
    cartridge_path = Path(args.cartridge_name)
    
    if not cartridge_path.exists():
        print(f"Error: Cartridge '{args.cartridge_name}' does not exist")
        return 1
    
    # Load existing cartridge
    generator = CartridgeGenerator("temp", "temp", verbose=False)  # Will be overridden during hydration
    if not generator.hydrate_from_existing_cartridge(args.cartridge_name):
        print("Failed to load existing cartridge")
        return 1
    
    # Find assignment by title
    try:
        assignment_settings = generator.df[
            (generator.df["type"] == "assignment_settings") & 
            (generator.df["title"] == args.title)
        ]
        
        if assignment_settings.empty:
            print(f"Error: Assignment '{args.title}' not found in cartridge")
            print("Available assignments:")
            all_assignments = generator.df[
                generator.df["type"] == "assignment_settings"
            ]["title"].tolist()
            if all_assignments:
                for assignment in all_assignments:
                    print(f"  - {assignment}")
            else:
                print("  (no assignments found)")
            return 1
        
        assignment_id = assignment_settings.iloc[0]["identifier"]
        
    except Exception as e:
        print(f"Error finding assignment: {e}")
        return 1
    
    # Update assignment
    try:
        print(f"Updating assignment '{args.title}' in cartridge '{args.cartridge_name}'")
        generator.update_assignment(
            assignment_id, 
            assignment_title=args.new_title,
            assignment_content=args.content,
            points=args.points,
            published=args.published,
            position=args.position
        )
        
        print(f"  Total components: {len(generator.df)}")
        
    except Exception as e:
        print(f"Error updating assignment: {e}")
        return 1
    
    return 0


def update_file(args):
    """Update a file in an existing cartridge"""
    cartridge_path = Path(args.cartridge_name)
    
    if not cartridge_path.exists():
        print(f"Error: Cartridge '{args.cartridge_name}' does not exist")
        return 1
    
    # Load existing cartridge
    generator = CartridgeGenerator("temp", "temp", verbose=False)  # Will be overridden during hydration
    if not generator.hydrate_from_existing_cartridge(args.cartridge_name):
        print("Failed to load existing cartridge")
        return 1
    
    # Find file by filename - files use type "resource" and href contains web_resources/filename
    try:
        file_resources = generator.df[
            (generator.df["type"] == "resource") & 
            (generator.df["href"].str.contains(f"web_resources/{args.filename}", na=False))
        ]
        
        if file_resources.empty:
            print(f"Error: File '{args.filename}' not found in cartridge")
            print("Available files:")
            all_files = generator.df[
                (generator.df["type"] == "resource") & 
                (generator.df["href"].str.contains("web_resources/", na=False))
            ]["href"].tolist()
            if all_files:
                for file_href in all_files:
                    filename = file_href.split("/")[-1] if "/" in file_href else file_href
                    print(f"  - {filename}")
            else:
                print("  (no files found)")
            return 1
        
        file_id = file_resources.iloc[0]["identifier"]
        
    except Exception as e:
        print(f"Error finding file: {e}")
        return 1
    
    # Update file
    try:
        print(f"Updating file '{args.filename}' in cartridge '{args.cartridge_name}'")
        generator.update_file(
            file_id, 
            filename=args.new_filename,
            file_content=args.content,
            position=args.position
        )
        
        print(f"  Total components: {len(generator.df)}")
        
    except Exception as e:
        print(f"Error updating file: {e}")
        return 1
    
    return 0


def delete_wiki(args):
    """Delete a wiki page from an existing cartridge"""
    cartridge_path = Path(args.cartridge_name)
    
    if not cartridge_path.exists():
        print(f"Error: Cartridge '{args.cartridge_name}' does not exist")
        return 1
    
    # Load existing cartridge
    generator = CartridgeGenerator("temp", "temp", verbose=False)  # Will be overridden during hydration
    if not generator.hydrate_from_existing_cartridge(args.cartridge_name):
        print("Failed to load existing cartridge")
        return 1
    
    # Find wiki page by title
    try:
        wiki_pages = generator.df[(generator.df["type"] == "wiki_page") & (generator.df["title"] == args.title)]
        if wiki_pages.empty:
            print(f"Error: Wiki page '{args.title}' not found in cartridge")
            print("Available wiki pages:")
            all_wiki_pages = generator.df[generator.df["type"] == "wiki_page"]["title"].tolist()
            if all_wiki_pages:
                for page in all_wiki_pages:
                    print(f"  - {page}")
            else:
                print("  (no wiki pages found)")
            return 1
        
        wiki_page_id = wiki_pages.iloc[0]["identifier"]
        
    except Exception as e:
        print(f"Error finding wiki page: {e}")
        return 1
    
    # Delete wiki page
    try:
        print(f"Deleting wiki page '{args.title}' from cartridge '{args.cartridge_name}'")
        generator.delete_wiki_page_by_id(wiki_page_id)
        
        print(f"✓ Wiki page '{args.title}' deleted successfully")
        print(f"  Total components: {len(generator.df)}")
        
    except Exception as e:
        print(f"Error deleting wiki page: {e}")
        return 1
    
    return 0


def delete_discussion(args):
    """Delete a discussion from an existing cartridge"""
    cartridge_path = Path(args.cartridge_name)
    
    if not cartridge_path.exists():
        print(f"Error: Cartridge '{args.cartridge_name}' does not exist")
        return 1
    
    # Load existing cartridge
    generator = CartridgeGenerator("temp", "temp", verbose=False)  # Will be overridden during hydration
    if not generator.hydrate_from_existing_cartridge(args.cartridge_name):
        print("Failed to load existing cartridge")
        return 1
    
    # Find discussion by title - discussions use type "resource" and identifierref lookup
    try:
        # First find resources with discussion-related type
        discussion_resources = generator.df[
            (generator.df["type"] == "resource") & 
            (generator.df["resource_type"] == "imsdt_xmlv1p1")
        ]
        
        # Then find module items that reference these resources and match the title
        discussion_items = generator.df[
            (generator.df["type"] == "module_item") & 
            (generator.df["title"] == args.title)
        ]
        
        if discussion_items.empty:
            print(f"Error: Discussion '{args.title}' not found in cartridge")
            print("Available discussions:")
            # Find all discussions by looking at module items with Discussion content type
            all_discussions = generator.df[
                (generator.df["type"] == "module_item") & 
                (generator.df["content_type"].isin(["DiscussionTopic", "Discussion"]))
            ]["title"].tolist()
            if all_discussions:
                for discussion in all_discussions:
                    print(f"  - {discussion}")
            else:
                print("  (no discussions found)")
            return 1
        
        # Get the identifierref from the module item to find the actual discussion resource
        discussion_item = discussion_items.iloc[0]
        discussion_id = discussion_item["identifierref"]
        
    except Exception as e:
        print(f"Error finding discussion: {e}")
        return 1
    
    # Delete discussion
    try:
        print(f"Deleting discussion '{args.title}' from cartridge '{args.cartridge_name}'")
        generator.delete_discussion_by_id(discussion_id)
        
        print(f"✓ Discussion '{args.title}' deleted successfully")
        print(f"  Total components: {len(generator.df)}")
        
    except Exception as e:
        print(f"Error deleting discussion: {e}")
        return 1
    
    return 0


def delete_assignment(args):
    """Delete an assignment from an existing cartridge"""
    cartridge_path = Path(args.cartridge_name)
    
    if not cartridge_path.exists():
        print(f"Error: Cartridge '{args.cartridge_name}' does not exist")
        return 1
    
    # Load existing cartridge
    generator = CartridgeGenerator("temp", "temp", verbose=False)  # Will be overridden during hydration
    if not generator.hydrate_from_existing_cartridge(args.cartridge_name):
        print("Failed to load existing cartridge")
        return 1
    
    # Find assignment by title - assignments use type "assignment_settings"
    try:
        assignment_settings = generator.df[
            (generator.df["type"] == "assignment_settings") & 
            (generator.df["title"] == args.title)
        ]
        
        if assignment_settings.empty:
            print(f"Error: Assignment '{args.title}' not found in cartridge")
            print("Available assignments:")
            # Find all assignments by looking at assignment_settings
            all_assignments = generator.df[
                generator.df["type"] == "assignment_settings"
            ]["title"].tolist()
            if all_assignments:
                for assignment in all_assignments:
                    print(f"  - {assignment}")
            else:
                print("  (no assignments found)")
            return 1
        
        assignment_id = assignment_settings.iloc[0]["identifier"]
        
    except Exception as e:
        print(f"Error finding assignment: {e}")
        return 1
    
    # Delete assignment
    try:
        print(f"Deleting assignment '{args.title}' from cartridge '{args.cartridge_name}'")
        generator.delete_assignment_by_id(assignment_id)
        
        print(f"✓ Assignment '{args.title}' deleted successfully")
        print(f"  Total components: {len(generator.df)}")
        
    except Exception as e:
        print(f"Error deleting assignment: {e}")
        return 1
    
    return 0


def delete_quiz(args):
    """Delete a quiz from an existing cartridge"""
    cartridge_path = Path(args.cartridge_name)
    
    if not cartridge_path.exists():
        print(f"Error: Cartridge '{args.cartridge_name}' does not exist")
        return 1
    
    # Load existing cartridge
    generator = CartridgeGenerator("temp", "temp", verbose=False)  # Will be overridden during hydration
    if not generator.hydrate_from_existing_cartridge(args.cartridge_name):
        print("Failed to load existing cartridge")
        return 1
    
    # Find quiz by title - quizzes use type "assessment_meta"
    try:
        quiz_assessments = generator.df[
            (generator.df["type"] == "assessment_meta") & 
            (generator.df["title"] == args.title)
        ]
        
        if quiz_assessments.empty:
            print(f"Error: Quiz '{args.title}' not found in cartridge")
            print("Available quizzes:")
            # Find all quizzes by looking at assessment_meta
            all_quizzes = generator.df[
                generator.df["type"] == "assessment_meta"
            ]["title"].tolist()
            if all_quizzes:
                for quiz in all_quizzes:
                    print(f"  - {quiz}")
            else:
                print("  (no quizzes found)")
            return 1
        
        quiz_id = quiz_assessments.iloc[0]["identifier"]
        
    except Exception as e:
        print(f"Error finding quiz: {e}")
        return 1
    
    # Delete quiz
    try:
        print(f"Deleting quiz '{args.title}' from cartridge '{args.cartridge_name}'")
        generator.delete_quiz_by_id(quiz_id)
        
        print(f"✓ Quiz '{args.title}' deleted successfully")
        print(f"  Total components: {len(generator.df)}")
        
    except Exception as e:
        print(f"Error deleting quiz: {e}")
        return 1
    
    return 0


def update_discussion(args):
    """Update a discussion in an existing cartridge"""
    cartridge_path = Path(args.cartridge_name)
    
    if not cartridge_path.exists():
        print(f"Error: Cartridge '{args.cartridge_name}' does not exist")
        return 1
    
    # Load existing cartridge
    generator = CartridgeGenerator("temp", "temp", verbose=False)  # Will be overridden during hydration
    if not generator.hydrate_from_existing_cartridge(args.cartridge_name):
        print("Failed to load existing cartridge")
        return 1
    
    # Find discussion by title - discussions use type "resource" with resource_type "imsdt_xmlv1p1"
    try:
        discussion_resources = generator.df[
            (generator.df["type"] == "resource") & 
            (generator.df["resource_type"] == "imsdt_xmlv1p1")
        ]
        
        # Find module items that reference these resources and match the title
        discussion_items = generator.df[
            (generator.df["type"] == "module_item") & 
            (generator.df["title"] == args.title)
        ]
        
        if discussion_items.empty:
            print(f"Error: Discussion '{args.title}' not found in cartridge")
            print("Available discussions:")
            all_discussions = generator.df[
                (generator.df["type"] == "module_item") & 
                (generator.df["content_type"].isin(["DiscussionTopic", "Discussion"]))
            ]["title"].tolist()
            if all_discussions:
                for discussion in all_discussions:
                    print(f"  - {discussion}")
            else:
                print("  (no discussions found)")
            return 1
        
        # Get the identifierref from the module item to find the actual discussion resource
        discussion_item = discussion_items.iloc[0]
        discussion_id = discussion_item["identifierref"]
        
    except Exception as e:
        print(f"Error finding discussion: {e}")
        return 1
    
    # Update discussion
    try:
        print(f"Updating discussion '{args.title}' in cartridge '{args.cartridge_name}'")
        generator.update_discussion(
            discussion_id, 
            title=args.new_title,
            body=args.content,
            published=args.published,
            position=args.position
        )
        
        print(f"  Total components: {len(generator.df)}")
        
    except Exception as e:
        print(f"Error updating discussion: {e}")
        return 1
    
    return 0


def update_quiz(args):
    """Update a quiz in an existing cartridge"""
    cartridge_path = Path(args.cartridge_name)
    
    if not cartridge_path.exists():
        print(f"Error: Cartridge '{args.cartridge_name}' does not exist")
        return 1
    
    # Load existing cartridge
    generator = CartridgeGenerator("temp", "temp", verbose=False)  # Will be overridden during hydration
    if not generator.hydrate_from_existing_cartridge(args.cartridge_name):
        print("Failed to load existing cartridge")
        return 1
    
    # Find quiz by title - quizzes use type "assessment_meta"
    try:
        quiz_assessments = generator.df[
            (generator.df["type"] == "assessment_meta") & 
            (generator.df["title"] == args.title)
        ]
        
        if quiz_assessments.empty:
            print(f"Error: Quiz '{args.title}' not found in cartridge")
            print("Available quizzes:")
            all_quizzes = generator.df[
                generator.df["type"] == "assessment_meta"
            ]["title"].tolist()
            if all_quizzes:
                for quiz in all_quizzes:
                    print(f"  - {quiz}")
            else:
                print("  (no quizzes found)")
            return 1
        
        quiz_id = quiz_assessments.iloc[0]["identifier"]
        
    except Exception as e:
        print(f"Error finding quiz: {e}")
        return 1
    
    # Update quiz
    try:
        print(f"Updating quiz '{args.title}' in cartridge '{args.cartridge_name}'")
        generator.update_quiz(
            quiz_id, 
            quiz_title=args.new_title,
            quiz_description=args.description,
            points=args.points,
            published=args.published,
            position=args.position
        )
        
        print(f"  Total components: {len(generator.df)}")
        
    except Exception as e:
        print(f"Error updating quiz: {e}")
        return 1
    
    return 0


def update_module(args):
    """Update a module in an existing cartridge"""
    cartridge_path = Path(args.cartridge_name)
    
    if not cartridge_path.exists():
        print(f"Error: Cartridge '{args.cartridge_name}' does not exist")
        return 1
    
    # Load existing cartridge
    generator = CartridgeGenerator("temp", "temp", verbose=False)  # Will be overridden during hydration
    if not generator.hydrate_from_existing_cartridge(args.cartridge_name):
        print("Failed to load existing cartridge")
        return 1
    
    # Find module by title - modules use type "module"
    try:
        module_rows = generator.df[
            (generator.df["type"] == "module") & 
            (generator.df["title"] == args.title)
        ]
        
        if module_rows.empty:
            print(f"Error: Module '{args.title}' not found in cartridge")
            print("Available modules:")
            all_modules = generator.df[
                generator.df["type"] == "module"
            ]["title"].tolist()
            if all_modules:
                for module in all_modules:
                    print(f"  - {module}")
            else:
                print("  (no modules found)")
            return 1
        
        module_id = module_rows.iloc[0]["identifier"]
        
    except Exception as e:
        print(f"Error finding module: {e}")
        return 1
    
    # Update module
    try:
        print(f"Updating module '{args.title}' in cartridge '{args.cartridge_name}'")
        
        # Check if we need to update the module
        if args.new_title is None and args.position is None:
            print("Error: At least one of --new-title or --position must be specified")
            return 1
        
        # If position is specified, call the new update_module_with_position method
        if args.position is not None:
            generator.update_module_with_position(module_id, args.new_title, args.position)
        else:
            # Only title update, use existing rename_module method
            generator.rename_module(module_id, args.new_title)
        
        print(f"  Total components: {len(generator.df)}")
        
    except Exception as e:
        print(f"Error updating module: {e}")
        return 1
    
    return 0


def delete_file(args):
    """Delete a file from an existing cartridge"""
    cartridge_path = Path(args.cartridge_name)
    
    if not cartridge_path.exists():
        print(f"Error: Cartridge '{args.cartridge_name}' does not exist")
        return 1
    
    # Load existing cartridge
    generator = CartridgeGenerator("temp", "temp", verbose=False)  # Will be overridden during hydration
    if not generator.hydrate_from_existing_cartridge(args.cartridge_name):
        print("Failed to load existing cartridge")
        return 1
    
    # Find file by filename - files use type "resource" and href contains web_resources/filename
    try:
        # Look for resources with href containing the filename in web_resources/
        file_resources = generator.df[
            (generator.df["type"] == "resource") & 
            (generator.df["href"].str.contains(f"web_resources/{args.filename}", na=False))
        ]
        
        if file_resources.empty:
            print(f"Error: File '{args.filename}' not found in cartridge")
            print("Available files:")
            # Find all files by looking at resources with web_resources/ in href
            all_files = generator.df[
                (generator.df["type"] == "resource") & 
                (generator.df["href"].str.contains("web_resources/", na=False))
            ]["href"].tolist()
            if all_files:
                for file_href in all_files:
                    # Extract just the filename from the href
                    filename = file_href.split("/")[-1] if "/" in file_href else file_href
                    print(f"  - {filename}")
            else:
                print("  (no files found)")
            return 1
        
        file_id = file_resources.iloc[0]["identifier"]
        
    except Exception as e:
        print(f"Error finding file: {e}")
        return 1
    
    # Delete file
    try:
        print(f"Deleting file '{args.filename}' from cartridge '{args.cartridge_name}'")
        generator.delete_file_by_id(file_id)
        
        print(f"✓ File '{args.filename}' deleted successfully")
        print(f"  Total components: {len(generator.df)}")
        
    except Exception as e:
        print(f"Error deleting file: {e}")
        return 1
    
    return 0


def delete_module(args):
    """Delete a module and all its contents from an existing cartridge"""
    cartridge_path = Path(args.cartridge_name)
    
    if not cartridge_path.exists():
        print(f"Error: Cartridge '{args.cartridge_name}' does not exist")
        return 1
    
    # Load existing cartridge
    generator = CartridgeGenerator("temp", "temp", verbose=False)  # Will be overridden during hydration
    if not generator.hydrate_from_existing_cartridge(args.cartridge_name):
        print("Failed to load existing cartridge")
        return 1
    
    # Find module by title
    try:
        module_row = generator.df[(generator.df["type"] == "module") & (generator.df["title"] == args.title)]
        if module_row.empty:
            print(f"Error: Module '{args.title}' not found in cartridge")
            print("Available modules:")
            modules = generator.df[generator.df["type"] == "module"]["title"].tolist()
            if modules:
                for module in modules:
                    print(f"  - {module}")
            else:
                print("  (no modules found)")
            return 1
        
        module_id = module_row.iloc[0]["identifier"]
        
    except Exception as e:
        print(f"Error finding module: {e}")
        return 1
    
    # Delete module
    try:
        print(f"Deleting module '{args.title}' and all its contents from cartridge '{args.cartridge_name}'")
        generator.delete_module_by_id(module_id)
        
        print(f"✓ Module '{args.title}' and all its contents deleted successfully")
        print(f"  Total components: {len(generator.df)}")
        
    except Exception as e:
        print(f"Error deleting module: {e}")
        return 1
    
    return 0


def display_wiki(args):
    """Display a wiki page's information by its title"""
    cartridge_path = Path(args.cartridge_name)
    
    if not cartridge_path.exists():
        print(f"Error: Cartridge '{args.cartridge_name}' does not exist")
        return 1
    
    # Load existing cartridge
    generator = CartridgeGenerator("temp", "temp", verbose=False)  # Will be overridden during hydration
    if not generator.hydrate_from_existing_cartridge(args.cartridge_name):
        print("Failed to load existing cartridge")
        return 1
    
    # Find wiki page by title
    try:
        wiki_pages = generator.df[(generator.df["type"] == "wiki_page") & (generator.df["title"] == args.title)]
        if wiki_pages.empty:
            print(f"Error: Wiki page '{args.title}' not found in cartridge")
            print("Available wiki pages:")
            all_wiki_pages = generator.df[generator.df["type"] == "wiki_page"]["title"].tolist()
            if all_wiki_pages:
                for page in all_wiki_pages:
                    print(f"  - {page}")
            else:
                print("  (no wiki pages found)")
            return 1
        
        wiki_page_id = wiki_pages.iloc[0]["identifier"]
        
    except Exception as e:
        print(f"Error finding wiki page: {e}")
        return 1
    
    # Display wiki page
    try:
        generator.display_wiki(wiki_page_id)
    except Exception as e:
        print(f"Error displaying wiki page: {e}")
        return 1
    
    return 0


def display_assignment(args):
    """Display an assignment's information by its title"""
    cartridge_path = Path(args.cartridge_name)
    
    if not cartridge_path.exists():
        print(f"Error: Cartridge '{args.cartridge_name}' does not exist")
        return 1
    
    # Load existing cartridge
    generator = CartridgeGenerator("temp", "temp", verbose=False)  # Will be overridden during hydration
    if not generator.hydrate_from_existing_cartridge(args.cartridge_name):
        print("Failed to load existing cartridge")
        return 1
    
    # Find assignment by title
    try:
        assignment_settings = generator.df[
            (generator.df["type"] == "assignment_settings") & 
            (generator.df["title"] == args.title)
        ]
        
        if assignment_settings.empty:
            print(f"Error: Assignment '{args.title}' not found in cartridge")
            print("Available assignments:")
            all_assignments = generator.df[
                generator.df["type"] == "assignment_settings"
            ]["title"].tolist()
            if all_assignments:
                for assignment in all_assignments:
                    print(f"  - {assignment}")
            else:
                print("  (no assignments found)")
            return 1
        
        assignment_id = assignment_settings.iloc[0]["identifier"]
        
    except Exception as e:
        print(f"Error finding assignment: {e}")
        return 1
    
    # Display assignment
    try:
        generator.display_assignment(assignment_id)
    except Exception as e:
        print(f"Error displaying assignment: {e}")
        return 1
    
    return 0


def display_quiz(args):
    """Display a quiz's information by its title"""
    cartridge_path = Path(args.cartridge_name)
    
    if not cartridge_path.exists():
        print(f"Error: Cartridge '{args.cartridge_name}' does not exist")
        return 1
    
    # Load existing cartridge
    generator = CartridgeGenerator("temp", "temp", verbose=False)  # Will be overridden during hydration
    if not generator.hydrate_from_existing_cartridge(args.cartridge_name):
        print("Failed to load existing cartridge")
        return 1
    
    # Find quiz by title - quizzes use type "assessment_meta"
    try:
        quiz_assessments = generator.df[
            (generator.df["type"] == "assessment_meta") & 
            (generator.df["title"] == args.title)
        ]
        
        if quiz_assessments.empty:
            print(f"Error: Quiz '{args.title}' not found in cartridge")
            print("Available quizzes:")
            all_quizzes = generator.df[
                generator.df["type"] == "assessment_meta"
            ]["title"].tolist()
            if all_quizzes:
                for quiz in all_quizzes:
                    print(f"  - {quiz}")
            else:
                print("  (no quizzes found)")
            return 1
        
        quiz_id = quiz_assessments.iloc[0]["identifier"]
        
    except Exception as e:
        print(f"Error finding quiz: {e}")
        return 1
    
    # Display quiz
    try:
        generator.display_quiz(quiz_id)
    except Exception as e:
        print(f"Error displaying quiz: {e}")
        return 1
    
    return 0


def display_discussion(args):
    """Display a discussion's information by its title"""
    cartridge_path = Path(args.cartridge_name)
    
    if not cartridge_path.exists():
        print(f"Error: Cartridge '{args.cartridge_name}' does not exist")
        return 1
    
    # Load existing cartridge
    generator = CartridgeGenerator("temp", "temp", verbose=False)  # Will be overridden during hydration
    if not generator.hydrate_from_existing_cartridge(args.cartridge_name):
        print("Failed to load existing cartridge")
        return 1
    
    # Find discussion by title - discussions use module items with Discussion content type
    try:
        discussion_items = generator.df[
            (generator.df["type"] == "module_item") & 
            (generator.df["title"] == args.title) &
            (generator.df["content_type"].isin(["DiscussionTopic", "Discussion"]))
        ]
        
        if discussion_items.empty:
            print(f"Error: Discussion '{args.title}' not found in cartridge")
            print("Available discussions:")
            all_discussions = generator.df[
                (generator.df["type"] == "module_item") & 
                (generator.df["content_type"].isin(["DiscussionTopic", "Discussion"]))
            ]["title"].tolist()
            if all_discussions:
                for discussion in all_discussions:
                    print(f"  - {discussion}")
            else:
                print("  (no discussions found)")
            return 1
        
        # Get the identifierref from the module item to find the actual discussion resource
        discussion_item = discussion_items.iloc[0]
        discussion_id = discussion_item["identifierref"]
        
    except Exception as e:
        print(f"Error finding discussion: {e}")
        return 1
    
    # Display discussion
    try:
        generator.display_discussion(discussion_id)
    except Exception as e:
        print(f"Error displaying discussion: {e}")
        return 1
    
    return 0


def display_file(args):
    """Display a file's information by its filename"""
    cartridge_path = Path(args.cartridge_name)
    
    if not cartridge_path.exists():
        print(f"Error: Cartridge '{args.cartridge_name}' does not exist")
        return 1
    
    # Load existing cartridge
    generator = CartridgeGenerator("temp", "temp", verbose=False)  # Will be overridden during hydration
    if not generator.hydrate_from_existing_cartridge(args.cartridge_name):
        print("Failed to load existing cartridge")
        return 1
    
    # Find file by filename - files use type "resource" and href contains web_resources/filename
    try:
        file_resources = generator.df[
            (generator.df["type"] == "resource") & 
            (generator.df["href"].str.contains(f"web_resources/{args.filename}", na=False))
        ]
        
        if file_resources.empty:
            print(f"Error: File '{args.filename}' not found in cartridge")
            print("Available files:")
            all_files = generator.df[
                (generator.df["type"] == "resource") & 
                (generator.df["href"].str.contains("web_resources/", na=False))
            ]["href"].tolist()
            if all_files:
                for file_href in all_files:
                    filename = file_href.split("/")[-1] if "/" in file_href else file_href
                    print(f"  - {filename}")
            else:
                print("  (no files found)")
            return 1
        
        file_id = file_resources.iloc[0]["identifier"]
        
    except Exception as e:
        print(f"Error finding file: {e}")
        return 1
    
    # Display file
    try:
        generator.display_file(file_id)
    except Exception as e:
        print(f"Error displaying file: {e}")
        return 1
    
    return 0




def package_cartridge(args):
    """Package cartridge into a zip file"""
    cartridge_path = Path(args.cartridge_name)
    
    if not cartridge_path.exists():
        print(f"Error: Cartridge '{args.cartridge_name}' does not exist")
        return 1
    
    print(f"Packaging cartridge '{args.cartridge_name}' into ZIP file...")
    zip_name = f"{args.cartridge_name}"
    shutil.make_archive(zip_name, 'zip', args.cartridge_name)
    
    print(f"✓ Cartridge packaged as '{zip_name}.zip'")
    
    return 0


def main():
    parser = argparse.ArgumentParser(description="Canvas Common Cartridge CLI Tool")
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Create command
    create_parser = subparsers.add_parser('create', help='Create a new cartridge')
    create_parser.add_argument('cartridge_name', help='Name of the cartridge directory to create')
    create_parser.add_argument('--title', required=True, help='Course title')
    create_parser.add_argument('--code', required=True, help='Course code')
    
    # Add-module command
    module_parser = subparsers.add_parser('add-module', help='Add a module to an existing cartridge')
    module_parser.add_argument('cartridge_name', help='Name of the cartridge directory')
    module_parser.add_argument('--title', required=True, help='Module title')
    module_parser.add_argument('--position', type=int, default=1, help='Module position (default: 1)')
    module_parser.add_argument('--published', type=bool, default=True, help='Whether module is published (default: True)')
    
    # Add-wiki command
    wiki_parser = subparsers.add_parser('add-wiki', help='Add a wiki page to a module')
    wiki_parser.add_argument('cartridge_name', help='Name of the cartridge directory')
    wiki_parser.add_argument('--module', required=True, help='Module title to add wiki page to')
    wiki_parser.add_argument('--title', required=True, help='Wiki page title')
    wiki_parser.add_argument('--content', required=True, help='Wiki page content')
    
    # Add-assignment command
    assignment_parser = subparsers.add_parser('add-assignment', help='Add an assignment to a module')
    assignment_parser.add_argument('cartridge_name', help='Name of the cartridge directory')
    assignment_parser.add_argument('--module', required=True, help='Module title to add assignment to')
    assignment_parser.add_argument('--title', required=True, help='Assignment title')
    assignment_parser.add_argument('--content', required=True, help='Assignment content/description')
    assignment_parser.add_argument('--points', type=int, default=100, help='Points possible (default: 100)')
    
    # Add-quiz command
    quiz_parser = subparsers.add_parser('add-quiz', help='Add a quiz to a module')
    quiz_parser.add_argument('cartridge_name', help='Name of the cartridge directory')
    quiz_parser.add_argument('--module', required=True, help='Module title to add quiz to')
    quiz_parser.add_argument('--title', required=True, help='Quiz title')
    quiz_parser.add_argument('--description', required=True, help='Quiz description')
    quiz_parser.add_argument('--points', type=int, default=10, help='Points possible (default: 10)')
    
    # Add-discussion command
    discussion_parser = subparsers.add_parser('add-discussion', help='Add a discussion to a module')
    discussion_parser.add_argument('cartridge_name', help='Name of the cartridge directory')
    discussion_parser.add_argument('--module', required=True, help='Module title to add discussion to')
    discussion_parser.add_argument('--title', required=True, help='Discussion title')
    discussion_parser.add_argument('--description', required=True, help='Discussion description/prompt')
    
    # Add-file command
    file_parser = subparsers.add_parser('add-file', help='Add a file to a module')
    file_parser.add_argument('cartridge_name', help='Name of the cartridge directory')
    file_parser.add_argument('--module', required=True, help='Module title to add file to')
    file_parser.add_argument('--filename', required=True, help='Filename')
    file_parser.add_argument('--content', required=True, help='File content')
    
    
    # List command
    list_parser = subparsers.add_parser('list', help='List contents of a cartridge')
    list_parser.add_argument('cartridge_name', help='Name of the cartridge directory')
    list_parser.add_argument('--json', action='store_true', help='Output only JSON format with no other text')
    
    # Update-wiki command
    update_wiki_parser = subparsers.add_parser('update-wiki', help='Update a wiki page in a cartridge')
    update_wiki_parser.add_argument('cartridge_name', help='Name of the cartridge directory')
    update_wiki_parser.add_argument('--title', required=True, help='Current wiki page title to update')
    update_wiki_parser.add_argument('--new-title', help='New wiki page title (optional)')
    update_wiki_parser.add_argument('--content', help='New wiki page content (optional)')
    update_wiki_parser.add_argument('--published', type=lambda x: x.lower() == 'true', help='Published status (true/false, optional)')
    update_wiki_parser.add_argument('--position', type=int, help='Position in module (optional)')
    
    # Copy-wiki command
    copy_wiki_parser = subparsers.add_parser('copy-wiki', help='Copy a wiki page to another module in a cartridge')
    copy_wiki_parser.add_argument('cartridge_name', help='Name of the cartridge directory')
    copy_wiki_parser.add_argument('--title', required=True, help='Wiki page title to copy')
    copy_wiki_parser.add_argument('--target-module', required=True, help='Target module title to copy wiki page to')
    
    # Copy-assignment command
    copy_assignment_parser = subparsers.add_parser('copy-assignment', help='Copy an assignment to another module in a cartridge')
    copy_assignment_parser.add_argument('cartridge_name', help='Name of the cartridge directory')
    copy_assignment_parser.add_argument('--title', required=True, help='Assignment title to copy')
    copy_assignment_parser.add_argument('--target-module', required=True, help='Target module title to copy assignment to')
    
    # Copy-discussion command
    copy_discussion_parser = subparsers.add_parser('copy-discussion', help='Copy a discussion to another module in a cartridge')
    copy_discussion_parser.add_argument('cartridge_name', help='Name of the cartridge directory')
    copy_discussion_parser.add_argument('--title', required=True, help='Discussion title to copy')
    copy_discussion_parser.add_argument('--target-module', required=True, help='Target module title to copy discussion to')
    
    # Copy-quiz command
    copy_quiz_parser = subparsers.add_parser('copy-quiz', help='Copy a quiz to another module in a cartridge')
    copy_quiz_parser.add_argument('cartridge_name', help='Name of the cartridge directory')
    copy_quiz_parser.add_argument('--title', required=True, help='Quiz title to copy')
    copy_quiz_parser.add_argument('--target-module', required=True, help='Target module title to copy quiz to')
    
    # Copy-file command
    copy_file_parser = subparsers.add_parser('copy-file', help='Copy a file to another module in a cartridge')
    copy_file_parser.add_argument('cartridge_name', help='Name of the cartridge directory')
    copy_file_parser.add_argument('--filename', required=True, help='Filename to copy')
    copy_file_parser.add_argument('--target-module', required=True, help='Target module title to copy file to')
    
    # Update-assignment command
    update_assignment_parser = subparsers.add_parser('update-assignment', help='Update an assignment in a cartridge')
    update_assignment_parser.add_argument('cartridge_name', help='Name of the cartridge directory')
    update_assignment_parser.add_argument('--title', required=True, help='Current assignment title to update')
    update_assignment_parser.add_argument('--new-title', help='New assignment title (optional)')
    update_assignment_parser.add_argument('--content', help='New assignment content (optional)')
    update_assignment_parser.add_argument('--points', type=int, help='Points possible (optional)')
    update_assignment_parser.add_argument('--published', type=lambda x: x.lower() == 'true', help='Published status (true/false, optional)')
    update_assignment_parser.add_argument('--position', type=int, help='Position in module (optional)')
    
    # Update-file command
    update_file_parser = subparsers.add_parser('update-file', help='Update a file in a cartridge')
    update_file_parser.add_argument('cartridge_name', help='Name of the cartridge directory')
    update_file_parser.add_argument('--filename', required=True, help='Current filename to update')
    update_file_parser.add_argument('--new-filename', help='New filename (optional)')
    update_file_parser.add_argument('--content', help='New file content (optional)')
    update_file_parser.add_argument('--position', type=int, help='Position in module (optional)')
    
    # Update-discussion command
    update_discussion_parser = subparsers.add_parser('update-discussion', help='Update a discussion in a cartridge')
    update_discussion_parser.add_argument('cartridge_name', help='Name of the cartridge directory')
    update_discussion_parser.add_argument('--title', required=True, help='Current discussion title to update')
    update_discussion_parser.add_argument('--new-title', help='New discussion title (optional)')
    update_discussion_parser.add_argument('--content', help='New discussion content/body (optional)')
    update_discussion_parser.add_argument('--published', type=lambda x: x.lower() == 'true', help='Published status (true/false, optional)')
    update_discussion_parser.add_argument('--position', type=int, help='Position in module (optional)')
    
    # Update-quiz command
    update_quiz_parser = subparsers.add_parser('update-quiz', help='Update a quiz in a cartridge')
    update_quiz_parser.add_argument('cartridge_name', help='Name of the cartridge directory')
    update_quiz_parser.add_argument('--title', required=True, help='Current quiz title to update')
    update_quiz_parser.add_argument('--new-title', help='New quiz title (optional)')
    update_quiz_parser.add_argument('--description', help='New quiz description (optional)')
    update_quiz_parser.add_argument('--points', type=int, help='Points possible (optional)')
    update_quiz_parser.add_argument('--published', type=lambda x: x.lower() == 'true', help='Published status (true/false, optional)')
    update_quiz_parser.add_argument('--position', type=int, help='Position in module (optional)')
    
    # Update-module command
    update_module_parser = subparsers.add_parser('update-module', help='Update a module in a cartridge')
    update_module_parser.add_argument('cartridge_name', help='Name of the cartridge directory')
    update_module_parser.add_argument('--title', required=True, help='Current module title to update')
    update_module_parser.add_argument('--new-title', help='New module title (optional)')
    update_module_parser.add_argument('--position', type=int, help='New position for the module (optional)')
    
    # Delete-wiki command
    delete_wiki_parser = subparsers.add_parser('delete-wiki', help='Delete a wiki page from a cartridge')
    delete_wiki_parser.add_argument('cartridge_name', help='Name of the cartridge directory')
    delete_wiki_parser.add_argument('--title', required=True, help='Wiki page title to delete')
    
    # Delete-discussion command
    delete_discussion_parser = subparsers.add_parser('delete-discussion', help='Delete a discussion from a cartridge')
    delete_discussion_parser.add_argument('cartridge_name', help='Name of the cartridge directory')
    delete_discussion_parser.add_argument('--title', required=True, help='Discussion title to delete')
    
    # Delete-assignment command
    delete_assignment_parser = subparsers.add_parser('delete-assignment', help='Delete an assignment from a cartridge')
    delete_assignment_parser.add_argument('cartridge_name', help='Name of the cartridge directory')
    delete_assignment_parser.add_argument('--title', required=True, help='Assignment title to delete')
    
    # Delete-quiz command
    delete_quiz_parser = subparsers.add_parser('delete-quiz', help='Delete a quiz from a cartridge')
    delete_quiz_parser.add_argument('cartridge_name', help='Name of the cartridge directory')
    delete_quiz_parser.add_argument('--title', required=True, help='Quiz title to delete')
    
    # Delete-file command
    delete_file_parser = subparsers.add_parser('delete-file', help='Delete a file from a cartridge')
    delete_file_parser.add_argument('cartridge_name', help='Name of the cartridge directory')
    delete_file_parser.add_argument('--filename', required=True, help='Filename to delete (e.g., "filename.txt")')
    
    # Delete-module command
    delete_module_parser = subparsers.add_parser('delete-module', help='Delete a module and all its contents from a cartridge')
    delete_module_parser.add_argument('cartridge_name', help='Name of the cartridge directory')
    delete_module_parser.add_argument('--title', required=True, help='Module title to delete')
    
    # Display-wiki command
    display_wiki_parser = subparsers.add_parser('display-wiki', help='Display a wiki page\'s information by title')
    display_wiki_parser.add_argument('cartridge_name', help='Name of the cartridge directory')
    display_wiki_parser.add_argument('--title', required=True, help='Wiki page title to display')
    
    # Display-assignment command
    display_assignment_parser = subparsers.add_parser('display-assignment', help='Display an assignment\'s information by title')
    display_assignment_parser.add_argument('cartridge_name', help='Name of the cartridge directory')
    display_assignment_parser.add_argument('--title', required=True, help='Assignment title to display')
    
    # Display-quiz command
    display_quiz_parser = subparsers.add_parser('display-quiz', help='Display a quiz\'s information by title')
    display_quiz_parser.add_argument('cartridge_name', help='Name of the cartridge directory')
    display_quiz_parser.add_argument('--title', required=True, help='Quiz title to display')
    
    # Display-discussion command
    display_discussion_parser = subparsers.add_parser('display-discussion', help='Display a discussion\'s information by title')
    display_discussion_parser.add_argument('cartridge_name', help='Name of the cartridge directory')
    display_discussion_parser.add_argument('--title', required=True, help='Discussion title to display')
    
    # Display-file command
    display_file_parser = subparsers.add_parser('display-file', help='Display a file\'s information by filename')
    display_file_parser.add_argument('cartridge_name', help='Name of the cartridge directory')
    display_file_parser.add_argument('--filename', required=True, help='Filename to display')
    
    # Package command
    package_parser = subparsers.add_parser('package', help='Package cartridge into ZIP file')
    package_parser.add_argument('cartridge_name', help='Name of the cartridge directory')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 1
    
    # Route to appropriate function
    if args.command == 'create':
        return create_cartridge(args)
    elif args.command == 'add-module':
        return add_module(args)
    elif args.command == 'add-wiki':
        return add_wiki(args)
    elif args.command == 'add-assignment':
        return add_assignment(args)
    elif args.command == 'add-quiz':
        return add_quiz(args)
    elif args.command == 'add-discussion':
        return add_discussion(args)
    elif args.command == 'add-file':
        return add_file(args)
    elif args.command == 'list':
        return list_cartridge(args)
    elif args.command == 'update-wiki':
        return update_wiki(args)
    elif args.command == 'copy-wiki':
        return copy_wiki(args)
    elif args.command == 'copy-assignment':
        return copy_assignment(args)
    elif args.command == 'copy-discussion':
        return copy_discussion(args)
    elif args.command == 'copy-quiz':
        return copy_quiz(args)
    elif args.command == 'copy-file':
        return copy_file(args)
    elif args.command == 'update-assignment':
        return update_assignment(args)
    elif args.command == 'update-file':
        return update_file(args)
    elif args.command == 'update-discussion':
        return update_discussion(args)
    elif args.command == 'update-quiz':
        return update_quiz(args)
    elif args.command == 'update-module':
        return update_module(args)
    elif args.command == 'delete-wiki':
        return delete_wiki(args)
    elif args.command == 'delete-discussion':
        return delete_discussion(args)
    elif args.command == 'delete-assignment':
        return delete_assignment(args)
    elif args.command == 'delete-quiz':
        return delete_quiz(args)
    elif args.command == 'delete-file':
        return delete_file(args)
    elif args.command == 'delete-module':
        return delete_module(args)
    elif args.command == 'display-wiki':
        return display_wiki(args)
    elif args.command == 'display-assignment':
        return display_assignment(args)
    elif args.command == 'display-quiz':
        return display_quiz(args)
    elif args.command == 'display-discussion':
        return display_discussion(args)
    elif args.command == 'display-file':
        return display_file(args)
    elif args.command == 'package':
        return package_cartridge(args)
    else:
        print(f"Unknown command: {args.command}")
        return 1


if __name__ == "__main__":
    sys.exit(main())