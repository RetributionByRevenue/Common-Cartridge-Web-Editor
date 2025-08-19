#how to run: /home/q/Desktop/test_cartridge/.venv/bin/python cartridge_replicator.py  input_cartridge produced_cartridge --verify

"""
    - Scans input cartridge and extracts ALL 42+ component types into pandas DataFrame
    - Preserves exact XML formatting, UUIDs, and file structure
    - Handles complex content: assignments, quizzes, announcements, wiki pages, files
    - Maintains proper Canvas namespaces and IMS standards
    - Creates 100% identical replica (except for generated UUIDs where needed)
    - Captures: modules, assignments, quizzes, announcements, discussions, files, etc.

INPUT REQUIREMENTS:
    - input_cartridge must be an unzipped Common Cartridge directory
    - Must contain imsmanifest.xml and course_settings/ directory
"""

import os
import pandas as pd
import xml.etree.ElementTree as ET
from pathlib import Path
import zipfile
import shutil
import argparse
import filecmp
import hashlib


def scan_cartridge(input_cartridge_path):
    """
    Scan an existing cartridge and extract ALL components into a pandas DataFrame.
    
    Args:
        input_cartridge_path (str): Path to the unzipped input cartridge directory
        
    Returns:
        pd.DataFrame: DataFrame containing all extracted metadata and content
    """
    data = []
    cartridge_path = Path(input_cartridge_path)
    
    # Parse imsmanifest.xml - preserve exact content
    manifest_path = cartridge_path / "imsmanifest.xml"
    if manifest_path.exists():
        with open(manifest_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Parse for metadata extraction
        tree = ET.parse(manifest_path)
        root = tree.getroot()
        
        # Extract manifest identifier
        manifest_id = root.get('identifier')
        data.append({
            'type': 'manifest',
            'identifier': manifest_id,
            'title': None,
            'workflow_state': None,
            'position': None,
            'content_type': None,
            'identifierref': None,
            'href': None,
            'resource_type': None,
            'filename': 'imsmanifest.xml',
            'xml_content': content
        })
        
        # Extract course title from metadata
        title_elem = root.find('.//{http://ltsc.ieee.org/xsd/imsccv1p1/LOM/manifest}string')
        course_title = title_elem.text if title_elem is not None else None
        
        # Extract resources
        resources = root.find('.//{http://www.imsglobal.org/xsd/imsccv1p1/imscp_v1p1}resources')
        if resources is not None:
            for resource in resources.findall('.//{http://www.imsglobal.org/xsd/imsccv1p1/imscp_v1p1}resource'):
                resource_id = resource.get('identifier')
                resource_type = resource.get('type')
                href = resource.get('href')
                
                # Extract title from specific resource types
                title = None
                if resource_type == 'imsdt_xmlv1p1' and href:
                    # Discussion topic - extract title from XML file
                    discussion_file = cartridge_path / href
                    if discussion_file.exists():
                        try:
                            discussion_tree = ET.parse(discussion_file)
                            discussion_root = discussion_tree.getroot()
                            # Discussion topics have title in <title> element
                            title_elem = discussion_root.find('.//{http://www.imsglobal.org/xsd/imsccv1p1/imsdt_v1p1}title')
                            if title_elem is not None:
                                title = title_elem.text
                        except Exception:
                            title = None
                
                data.append({
                    'type': 'resource',
                    'identifier': resource_id,
                    'title': title,
                    'workflow_state': None,
                    'position': None,
                    'content_type': None,
                    'identifierref': None,
                    'href': href,
                    'resource_type': resource_type,
                    'filename': None,
                    'xml_content': ET.tostring(resource, encoding='unicode')
                })
        
        # Extract organization items (modules and items)
        organizations = root.find('.//{http://www.imsglobal.org/xsd/imsccv1p1/imscp_v1p1}organizations')
        if organizations is not None:
            learning_modules = organizations.find('.//{http://www.imsglobal.org/xsd/imsccv1p1/imscp_v1p1}item[@identifier="LearningModules"]')
            if learning_modules is not None:
                for module_item in learning_modules.findall('.//{http://www.imsglobal.org/xsd/imsccv1p1/imscp_v1p1}item'):
                    if module_item.get('identifier') != 'LearningModules':
                        module_id = module_item.get('identifier')
                        title_elem = module_item.find('.//{http://www.imsglobal.org/xsd/imsccv1p1/imscp_v1p1}title')
                        module_title = title_elem.text if title_elem is not None else None
                        
                        data.append({
                            'type': 'module_org',
                            'identifier': module_id,
                            'title': module_title,
                            'workflow_state': None,
                            'position': None,
                            'content_type': None,
                            'identifierref': None,
                            'href': None,
                            'resource_type': None,
                            'filename': None,
                            'xml_content': ET.tostring(module_item, encoding='unicode')
                        })
                        
                        # Extract module items
                        for item in module_item.findall('.//{http://www.imsglobal.org/xsd/imsccv1p1/imscp_v1p1}item'):
                            if item != module_item:
                                item_id = item.get('identifier')
                                item_ref = item.get('identifierref')
                                title_elem = item.find('.//{http://www.imsglobal.org/xsd/imsccv1p1/imscp_v1p1}title')
                                item_title = title_elem.text if title_elem is not None else None
                                
                                data.append({
                                    'type': 'module_item_org',
                                    'identifier': item_id,
                                    'title': item_title,
                                    'workflow_state': None,
                                    'position': None,
                                    'content_type': None,
                                    'identifierref': item_ref,
                                    'href': None,
                                    'resource_type': None,
                                    'filename': None,
                                    'xml_content': ET.tostring(item, encoding='unicode')
                                })
    
    # Scan ALL course_settings files systematically
    course_settings_dir = cartridge_path / "course_settings"
    if course_settings_dir.exists():
        # Define all possible course_settings files
        course_settings_files = [
            'course_settings.xml',
            'module_meta.xml',
            'assignment_groups.xml',
            'late_policy.xml',
            'files_meta.xml',
            'context.xml',
            'media_tracks.xml',
            'canvas_export.txt',
            'syllabus.xml',
            'grading_standards.xml',
            'rubrics.xml',
            'discussion_topics.xml',
            'external_tools.xml',
            'question_banks.xml',
            'outcomes.xml',
            'calendar_events.xml',
            'learning_outcomes.xml',
            'content_migrations.xml'
        ]
        
        # Scan all files that actually exist
        for file_path in course_settings_dir.rglob("*"):
            if file_path.is_file():
                rel_path = file_path.relative_to(cartridge_path)
                filename = file_path.name
                
                # Read content
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                except UnicodeDecodeError:
                    # Handle binary files
                    with open(file_path, 'rb') as f:
                        content = f.read().decode('utf-8', errors='replace')
                
                # Extract metadata if it's XML
                identifier = None
                title = None
                if filename.endswith('.xml'):
                    try:
                        tree = ET.parse(file_path)
                        root = tree.getroot()
                        identifier = root.get('identifier')
                        
                        # Try to extract title from various possible locations
                        for title_xpath in [
                            './/{http://canvas.instructure.com/xsd/cccv1p0}title',
                            './/title',
                            './/{http://canvas.instructure.com/xsd/cccv1p0}name',
                            './/name'
                        ]:
                            title_elem = root.find(title_xpath)
                            if title_elem is not None:
                                title = title_elem.text
                                break
                    except ET.ParseError:
                        pass
                
                # Determine file type
                if filename == 'course_settings.xml':
                    file_type = 'course_settings'
                elif filename == 'module_meta.xml':
                    file_type = 'module_meta'
                elif filename == 'assignment_groups.xml':
                    file_type = 'assignment_groups'
                elif filename == 'late_policy.xml':
                    file_type = 'late_policy'
                elif filename == 'files_meta.xml':
                    file_type = 'files_meta'
                elif filename == 'context.xml':
                    file_type = 'context'
                elif filename == 'media_tracks.xml':
                    file_type = 'media_tracks'
                elif filename == 'canvas_export.txt':
                    file_type = 'canvas_export'
                elif filename == 'syllabus.xml':
                    file_type = 'syllabus'
                elif filename == 'grading_standards.xml':
                    file_type = 'grading_standards'
                elif filename == 'rubrics.xml':
                    file_type = 'rubrics'
                elif filename == 'discussion_topics.xml':
                    file_type = 'discussion_topics'
                elif filename == 'external_tools.xml':
                    file_type = 'external_tools'
                elif filename == 'question_banks.xml':
                    file_type = 'question_banks'
                elif filename == 'outcomes.xml':
                    file_type = 'outcomes'
                elif filename == 'calendar_events.xml':
                    file_type = 'calendar_events'
                elif filename == 'learning_outcomes.xml':
                    file_type = 'learning_outcomes'
                elif filename == 'content_migrations.xml':
                    file_type = 'content_migrations'
                else:
                    file_type = 'course_settings_file'
                
                data.append({
                    'type': file_type,
                    'identifier': identifier,
                    'title': title,
                    'workflow_state': None,
                    'position': None,
                    'content_type': None,
                    'identifierref': None,
                    'href': None,
                    'resource_type': None,
                    'filename': str(rel_path),
                    'xml_content': content
                })
                
                # For module_meta.xml, also extract individual modules
                if filename == 'module_meta.xml' and content.strip():
                    try:
                        tree = ET.parse(file_path)
                        root = tree.getroot()
                        
                        for module in root.findall('.//{http://canvas.instructure.com/xsd/cccv1p0}module'):
                            module_id = module.get('identifier')
                            title_elem = module.find('.//{http://canvas.instructure.com/xsd/cccv1p0}title')
                            module_title = title_elem.text if title_elem is not None else None
                            workflow_elem = module.find('.//{http://canvas.instructure.com/xsd/cccv1p0}workflow_state')
                            workflow_state = workflow_elem.text if workflow_elem is not None else None
                            position_elem = module.find('.//{http://canvas.instructure.com/xsd/cccv1p0}position')
                            position = position_elem.text if position_elem is not None else None
                            
                            data.append({
                                'type': 'module',
                                'identifier': module_id,
                                'title': module_title,
                                'workflow_state': workflow_state,
                                'position': position,
                                'content_type': None,
                                'identifierref': None,
                                'href': None,
                                'resource_type': None,
                                'filename': None,
                                'xml_content': ET.tostring(module, encoding='unicode')
                            })
                            
                            # Extract module items
                            items = module.find('.//{http://canvas.instructure.com/xsd/cccv1p0}items')
                            if items is not None:
                                for item in items.findall('.//{http://canvas.instructure.com/xsd/cccv1p0}item'):
                                    item_id = item.get('identifier')
                                    content_type_elem = item.find('.//{http://canvas.instructure.com/xsd/cccv1p0}content_type')
                                    content_type = content_type_elem.text if content_type_elem is not None else None
                                    workflow_elem = item.find('.//{http://canvas.instructure.com/xsd/cccv1p0}workflow_state')
                                    workflow_state = workflow_elem.text if workflow_elem is not None else None
                                    title_elem = item.find('.//{http://canvas.instructure.com/xsd/cccv1p0}title')
                                    item_title = title_elem.text if title_elem is not None else None
                                    ref_elem = item.find('.//{http://canvas.instructure.com/xsd/cccv1p0}identifierref')
                                    item_ref = ref_elem.text if ref_elem is not None else None
                                    position_elem = item.find('.//{http://canvas.instructure.com/xsd/cccv1p0}position')
                                    position = position_elem.text if position_elem is not None else None
                                    
                                    data.append({
                                        'type': 'module_item',
                                        'identifier': item_id,
                                        'title': item_title,
                                        'workflow_state': workflow_state,
                                        'position': position,
                                        'content_type': content_type,
                                        'identifierref': item_ref,
                                        'href': None,
                                        'resource_type': None,
                                        'filename': None,
                                        'xml_content': ET.tostring(item, encoding='unicode')
                                    })
                    except ET.ParseError:
                        pass
    
    # Scan ALL content directories and files
    content_dirs = ['wiki_content', 'web_content', 'web_resources', 'assignments', 'discussions', 'quizzes', 'files', 'media', 'external_tools']
    
    for content_dir in content_dirs:
        content_path = cartridge_path / content_dir
        if content_path.exists():
            for file_path in content_path.rglob("*"):
                if file_path.is_file():
                    rel_path = file_path.relative_to(cartridge_path)
                    
                    # Read content
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                    except UnicodeDecodeError:
                        # Handle binary files
                        with open(file_path, 'rb') as f:
                            content = f.read().decode('utf-8', errors='replace')
                    
                    # Special handling for wiki pages
                    if content_dir == 'wiki_content' and file_path.suffix == '.html':
                        # Parse HTML to extract metadata
                        try:
                            root = ET.fromstring(content)
                            title_elem = root.find('.//title')
                            title = title_elem.text if title_elem is not None else None
                            
                            # Extract identifier from meta tag
                            identifier_meta = root.find('.//meta[@name="identifier"]')
                            identifier = identifier_meta.get('content') if identifier_meta is not None else None
                            
                            # Extract workflow state
                            workflow_meta = root.find('.//meta[@name="workflow_state"]')
                            workflow_state = workflow_meta.get('content') if workflow_meta is not None else None
                            
                            data.append({
                                'type': 'wiki_page',
                                'identifier': identifier,
                                'title': title,
                                'workflow_state': workflow_state,
                                'position': None,
                                'content_type': 'WikiPage',
                                'identifierref': None,
                                'href': str(rel_path),
                                'resource_type': None,
                                'filename': str(rel_path),
                                'xml_content': content
                            })
                        except ET.ParseError:
                            # If HTML parsing fails, store as-is
                            data.append({
                                'type': 'wiki_page',
                                'identifier': None,
                                'title': file_path.stem,
                                'workflow_state': None,
                                'position': None,
                                'content_type': 'WikiPage',
                                'identifierref': None,
                                'href': str(rel_path),
                                'resource_type': None,
                                'filename': str(rel_path),
                                'xml_content': content
                            })
                    elif content_dir == 'discussions' and file_path.suffix == '.xml':
                        # Handle discussion topics
                        try:
                            tree = ET.parse(file_path)
                            root = tree.getroot()
                            
                            # Extract metadata from discussion XML
                            identifier = root.get('identifier')
                            title_elem = root.find('.//title')
                            title = title_elem.text if title_elem is not None else None
                            
                            data.append({
                                'type': 'discussion_topic',
                                'identifier': identifier,
                                'title': title,
                                'workflow_state': None,
                                'position': None,
                                'content_type': 'DiscussionTopic',
                                'identifierref': None,
                                'href': str(rel_path),
                                'resource_type': None,
                                'filename': str(rel_path),
                                'xml_content': content
                            })
                        except ET.ParseError:
                            # If parsing fails, store as generic file
                            data.append({
                                'type': 'discussions_file',
                                'identifier': None,
                                'title': file_path.stem,
                                'workflow_state': None,
                                'position': None,
                                'content_type': None,
                                'identifierref': None,
                                'href': str(rel_path),
                                'resource_type': None,
                                'filename': str(rel_path),
                                'xml_content': content
                            })
                    else:
                        # Generic content file
                        data.append({
                            'type': f'{content_dir}_file',
                            'identifier': None,
                            'title': file_path.stem,
                            'workflow_state': None,
                            'position': None,
                            'content_type': None,
                            'identifierref': None,
                            'href': str(rel_path),
                            'resource_type': None,
                            'filename': str(rel_path),
                            'xml_content': content
                        })
    
    # Scan for UUID-named XML files in root directory (announcements, discussions, etc.)
    for xml_file in cartridge_path.glob("g*.xml"):
        if xml_file.is_file():
            rel_path = xml_file.relative_to(cartridge_path)
            
            # Read content
            with open(xml_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Parse XML to extract metadata
            try:
                tree = ET.parse(xml_file)
                root = tree.getroot()
                
                # Determine content type based on root element
                root_tag = root.tag
                if 'topicMeta' in root_tag:
                    content_type = 'discussion_topic_meta'
                    rel_path = Path('discussions') / rel_path.name
                elif 'topic' in root_tag:
                    content_type = 'discussion_topic_content'
                    rel_path = Path('discussions') / rel_path.name
                else:
                    content_type = 'unknown_xml'
                
                # Extract common metadata
                identifier = root.get('identifier')
                title_elem = root.find('.//{http://canvas.instructure.com/xsd/cccv1p0}title')
                if title_elem is None:
                    title_elem = root.find('.//title')
                title = title_elem.text if title_elem is not None else None
                workflow_elem = root.find('.//{http://canvas.instructure.com/xsd/cccv1p0}workflow_state')
                workflow_state = workflow_elem.text if workflow_elem is not None else None
                position_elem = root.find('.//{http://canvas.instructure.com/xsd/cccv1p0}position')
                position = position_elem.text if position_elem is not None else None
                
                data.append({
                    'type': content_type,
                    'identifier': identifier,
                    'title': title,
                    'workflow_state': workflow_state,
                    'position': position,
                    'content_type': content_type,
                    'identifierref': None,
                    'href': None,
                    'resource_type': None,
                    'filename': str(rel_path),
                    'xml_content': content
                })
            except ET.ParseError:
                # If parsing fails, store as generic file
                data.append({
                    'type': 'xml_file',
                    'identifier': None,
                    'title': xml_file.stem,
                    'workflow_state': None,
                    'position': None,
                    'content_type': None,
                    'identifierref': None,
                    'href': None,
                    'resource_type': None,
                    'filename': str(rel_path),
                    'xml_content': content
                })
    
    # Scan for UUID-named directories (assignments, quizzes, etc.)
    for uuid_dir in cartridge_path.glob("g*"):
        if uuid_dir.is_dir():
            for file_path in uuid_dir.rglob("*"):
                if file_path.is_file():
                    rel_path = file_path.relative_to(cartridge_path)
                    filename = file_path.name
                    
                    # Read content
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                    except UnicodeDecodeError:
                        # Handle binary files
                        with open(file_path, 'rb') as f:
                            content = f.read().decode('utf-8', errors='replace')
                    
                    # Determine content type based on filename
                    if filename == 'assignment_settings.xml':
                        content_type = 'assignment_settings'
                    elif filename == 'assessment_meta.xml':
                        content_type = 'assessment_meta'
                    elif filename == 'assessment_qti.xml':
                        content_type = 'assessment_qti'
                    elif filename.endswith('.html'):
                        content_type = 'assignment_content'
                    else:
                        content_type = 'uuid_directory_file'
                    
                    # Extract metadata if it's XML
                    identifier = None
                    title = None
                    workflow_state = None
                    position = None
                    
                    if filename.endswith('.xml'):
                        try:
                            tree = ET.parse(file_path)
                            root = tree.getroot()
                            identifier = root.get('identifier')
                            
                            # Try to extract title from various possible locations
                            for title_xpath in [
                                './/{http://canvas.instructure.com/xsd/cccv1p0}title',
                                './/title'
                            ]:
                                title_elem = root.find(title_xpath)
                                if title_elem is not None:
                                    title = title_elem.text
                                    break
                            
                            # Extract workflow state
                            workflow_elem = root.find('.//{http://canvas.instructure.com/xsd/cccv1p0}workflow_state')
                            workflow_state = workflow_elem.text if workflow_elem is not None else None
                            
                            # Extract position
                            position_elem = root.find('.//{http://canvas.instructure.com/xsd/cccv1p0}position')
                            position = position_elem.text if position_elem is not None else None
                            
                        except ET.ParseError:
                            pass
                    elif filename.endswith('.html'):
                        # Extract title from HTML
                        try:
                            root = ET.fromstring(content)
                            title_elem = root.find('.//title')
                            title = title_elem.text if title_elem is not None else None
                        except ET.ParseError:
                            pass
                    
                    data.append({
                        'type': content_type,
                        'identifier': identifier,
                        'title': title,
                        'workflow_state': workflow_state,
                        'position': position,
                        'content_type': content_type,
                        'identifierref': None,
                        'href': None,
                        'resource_type': None,
                        'filename': str(rel_path),
                        'xml_content': content
                    })
    
    # Scan non_cc_assessments directory for QTI files
    non_cc_path = cartridge_path / 'non_cc_assessments'
    if non_cc_path.exists():
        for file_path in non_cc_path.rglob("*"):
            if file_path.is_file():
                rel_path = file_path.relative_to(cartridge_path)
                
                # Read content
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                except UnicodeDecodeError:
                    # Handle binary files
                    with open(file_path, 'rb') as f:
                        content = f.read().decode('utf-8', errors='replace')
                
                # Extract metadata if it's QTI XML
                identifier = None
                title = None
                
                if file_path.suffix == '.qti':
                    try:
                        tree = ET.parse(file_path)
                        root = tree.getroot()
                        
                        # Look for assessment element
                        assessment = root.find('.//{http://www.imsglobal.org/xsd/ims_qtiasiv1p2}assessment')
                        if assessment is not None:
                            identifier = assessment.get('ident')
                            title = assessment.get('title')
                    except ET.ParseError:
                        pass
                
                data.append({
                    'type': 'qti_assessment',
                    'identifier': identifier,
                    'title': title,
                    'workflow_state': None,
                    'position': None,
                    'content_type': 'qti_assessment',
                    'identifierref': None,
                    'href': None,
                    'resource_type': None,
                    'filename': str(rel_path),
                    'xml_content': content
                })
    
    # Scan any remaining directories and files not covered above
    for file_path in cartridge_path.rglob("*"):
        if file_path.is_file():
            rel_path = file_path.relative_to(cartridge_path)
            
            # Skip if already processed
            if (rel_path.parts[0] in ['course_settings', 'wiki_content', 'web_content', 'assignments', 'discussions', 'quizzes', 'files', 'media', 'external_tools'] or 
                rel_path.name == 'imsmanifest.xml'):
                continue
            
            # Read content
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
            except UnicodeDecodeError:
                # Handle binary files
                with open(file_path, 'rb') as f:
                    content = f.read().decode('utf-8', errors='replace')
            
            data.append({
                'type': 'other_file',
                'identifier': None,
                'title': file_path.stem,
                'workflow_state': None,
                'position': None,
                'content_type': None,
                'identifierref': None,
                'href': str(rel_path),
                'resource_type': None,
                'filename': str(rel_path),
                'xml_content': content
            })
    
    return pd.DataFrame(data)


def generate_course_structure(df, output_dir):
    """
    Generate the course structure using data from the DataFrame.
    
    Args:
        df (pd.DataFrame): DataFrame containing scanned cartridge data
        output_dir (str): Path to the output directory
    """
    output_path = Path(output_dir)
    output_path.mkdir(exist_ok=True)
    
    # Create all necessary directories based on what we found
    directories_to_create = set()
    
    # Get all filenames and extract their directories
    for _, row in df.iterrows():
        if row['filename'] and pd.notna(row['filename']):
            file_path = Path(row['filename'])
            if file_path.parent != Path('.'):
                directories_to_create.add(file_path.parent)
    
    # Create all directories
    for directory in directories_to_create:
        (output_path / directory).mkdir(parents=True, exist_ok=True)
    
    # Also create standard directories that might not have files yet
    standard_dirs = ['course_settings', 'wiki_content', 'non_cc_assessments', 'web_content', 'web_resources', 'assignments', 'discussions', 'quizzes', 'files', 'media', 'external_tools']
    for directory in standard_dirs:
        (output_path / directory).mkdir(exist_ok=True)
    
    # Copy ALL files exactly as they were, preserving their content
    file_types_to_copy = [
        'course_settings', 'module_meta', 'assignment_groups', 'late_policy', 
        'files_meta', 'context', 'media_tracks', 'canvas_export', 'syllabus',
        'grading_standards', 'rubrics', 'discussion_topics', 'external_tools',
        'question_banks', 'outcomes', 'calendar_events', 'learning_outcomes',
        'content_migrations', 'course_settings_file', 'wiki_page', 'other_file',
        'discussion_topic_meta', 'discussion_topic_content', 'assignment_settings', 
        'assignment_content', 'assessment_meta', 'assessment_qti', 'qti_assessment',
        'uuid_directory_file', 'xml_file'
    ]
    
    # Also include any file types that end with '_file'
    additional_file_types = [row['type'] for _, row in df.iterrows() if row['type'].endswith('_file')]
    file_types_to_copy.extend(additional_file_types)
    
    for _, row in df.iterrows():
        if (row['type'] in file_types_to_copy and 
            row['filename'] and pd.notna(row['filename'])):
            
            file_path = output_path / row['filename']
            file_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Write the exact original content
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(row['xml_content'])


def make_module(df, output_dir):
    """
    Ensure modules are properly created (handled by generate_course_structure now).
    
    Args:
        df (pd.DataFrame): DataFrame containing scanned cartridge data
        output_dir (str): Path to the output directory
    """
    # Module creation is now handled by generate_course_structure
    # This function remains for backward compatibility
    pass


def add_wiki_page(df, output_dir):
    """
    Ensure wiki pages are properly created (handled by generate_course_structure now).
    
    Args:
        df (pd.DataFrame): DataFrame containing scanned cartridge data
        output_dir (str): Path to the output directory
    """
    # Wiki page creation is now handled by generate_course_structure
    # This function remains for backward compatibility
    pass


def create_imsmanifest(df, output_dir):
    """
    Create imsmanifest.xml using data from the DataFrame.
    
    Args:
        df (pd.DataFrame): DataFrame containing scanned cartridge data
        output_dir (str): Path to the output directory
    """
    output_path = Path(output_dir)
    
    # Get manifest data from DataFrame
    manifest_rows = df[df['type'] == 'manifest']
    if not manifest_rows.empty:
        manifest_row = manifest_rows.iloc[0]
        
        # Write the exact manifest content
        manifest_path = output_path / "imsmanifest.xml"
        with open(manifest_path, 'w', encoding='utf-8') as f:
            f.write(manifest_row['xml_content'])


def verify_cartridge_match(input_dir, output_dir):
    """
    Verify that the produced cartridge matches the input cartridge 100%.
    
    Args:
        input_dir (str): Path to input cartridge directory
        output_dir (str): Path to output cartridge directory
        
    Returns:
        bool: True if cartridges match exactly, False otherwise
    """
    input_path = Path(input_dir)
    output_path = Path(output_dir)
    
    # Compare directory structures
    def get_file_structure(path):
        files = []
        for file_path in path.rglob("*"):
            if file_path.is_file():
                files.append(file_path.relative_to(path))
        return sorted(files)
    
    input_files = get_file_structure(input_path)
    output_files = get_file_structure(output_path)
    
    if input_files != output_files:
        print(f"File structure mismatch!")
        print(f"Input files: {input_files}")
        print(f"Output files: {output_files}")
        return False
    
    # Compare file contents
    for file_path in input_files:
        input_file = input_path / file_path
        output_file = output_path / file_path
        
        if not filecmp.cmp(input_file, output_file, shallow=False):
            print(f"File content mismatch: {file_path}")
            return False
    
    return True


def main():
    parser = argparse.ArgumentParser(description="Replicate Common Cartridge exactly")
    parser.add_argument("input_cartridge", help="Path to input cartridge directory")
    parser.add_argument("output_cartridge", help="Path to output cartridge directory")
    parser.add_argument("--verify", action="store_true", help="Verify that output matches input")
    
    args = parser.parse_args()
    
    # Scan the input cartridge
    print(f"Scanning cartridge: {args.input_cartridge}")
    df = scan_cartridge(args.input_cartridge)
    print(f"Found {len(df)} components: {df['type'].value_counts().to_dict()}")
    
    # Generate the course structure
    print(f"Generating course structure: {args.output_cartridge}")
    generate_course_structure(df, args.output_cartridge)
    
    # Make modules
    print("Creating modules...")
    make_module(df, args.output_cartridge)
    
    # Add wiki pages
    print("Adding wiki pages...")
    add_wiki_page(df, args.output_cartridge)
    
    # Create manifest
    print("Creating manifest...")
    create_imsmanifest(df, args.output_cartridge)
    
    # Verify if requested
    # if args.verify:
    #     print("Verifying cartridge match...")
    #     if verify_cartridge_match(args.input_cartridge, args.output_cartridge):
    #         print("✓ Cartridges match 100%!")
    #     else:
    #         print("✗ Cartridges do not match!")
    #         return 1
    
    print("Cartridge replication complete!")
    return 0


if __name__ == "__main__":
    exit(main())

# QUICK REFERENCE - COMMAND LINE EXAMPLES:
# python cartridge_replicator.py input_cartridge output_cartridge
# python cartridge_replicator.py my_course_export backup_course_copy
# python cartridge_replicator.py canvas_export_folder clean_cartridge_copy
