#!/usr/bin/env python3
# Command to run this file: /home/q/Desktop/test_cartridge/.venv/bin/python cartridge_generator.py generated_cartridge (deprecated)

import os
import uuid
import xml.etree.ElementTree as ET
from pathlib import Path
from datetime import datetime
import filecmp
import shutil
import random
from .replicator import scan_cartridge
from ._cartridge_deletion_mixin import CartridgeDeletionMixin
from ._cartridge_update_mixin import CartridgeUpdateMixin
from ._cartridge_display_mixin import CartridgeDisplayMixin
from ._cartridge_add_mixin import CartridgeAddMixin
from ._cartridge_standalone_add_mixin import CartridgeStandaloneAddMixin
from ._cartridge_copy_mixin import CartridgeCopyMixin
from ._cartridge_hydrator_mixin import CartridgeHydratorMixin

class CartridgeGenerator(CartridgeDeletionMixin, CartridgeUpdateMixin, CartridgeDisplayMixin, CartridgeAddMixin, CartridgeStandaloneAddMixin, CartridgeCopyMixin, CartridgeHydratorMixin):
    def __init__(self, course_title="Generated Course", course_code="GEN101", verbose=True):
        self.course_title = course_title
        self.course_code = course_code
        self.verbose = verbose
        
        # Generate main identifiers
        self.course_id = f"g{uuid.uuid4().hex}"
        self.manifest_id = f"g{uuid.uuid4().hex}"
        self.root_account_uuid = f"ff2e5780-fa5b-012d-f7b3-{uuid.uuid4().hex[:12]}"
        
        # Storage for generated content
        self.modules = []
        self.assignments = []
        self.quizzes = []
        self.announcements = []
        self.wiki_pages = []
        self.files = []
        self.resources = []
        self.organization_items = []
        
        # Assignment group ID (required for assignments/quizzes)
        self.assignment_group_id = f"g{uuid.uuid4().hex}"
        
        # Store current cartridge state and DataFrame
        self.output_dir = None
        self.current_df = None
    
    @property
    def df(self):
        """Get the current DataFrame state"""
        return self.current_df
    
    def _update_cartridge_state(self):
        """Write cartridge files and update DataFrame state"""
        if self.output_dir:
            self.write_cartridge_files(self.output_dir)
            self.current_df = scan_cartridge(self.output_dir)
            
            # Remove duplicates based on identifier and type
            if self.current_df is not None and not self.current_df.empty:
                # Keep only the last occurrence of each identifier+type combination
                self.current_df = self.current_df.drop_duplicates(
                    subset=['identifier', 'type'], 
                    keep='last'
                ).reset_index(drop=True)
            
            if getattr(self, 'verbose', True):
                print(f"Cartridge state updated. Found {len(self.current_df)} components.")
        
    def create_base_cartridge(self, output_dir):
        """Create the base cartridge structure with core files"""
        output_path = Path(output_dir)
        
        # Remove existing contents if directory is not empty
        if output_path.exists() and any(output_path.iterdir()):
            print(f"Removing existing contents from {output_dir}")
            shutil.rmtree(output_path)
        
        output_path.mkdir(exist_ok=True)
        
        # Create directory structure
        directories = [
            'course_settings', 'wiki_content', 'non_cc_assessments', 
            'web_resources', 'assignments', 'discussions', 'quizzes', 
            'files', 'media', 'external_tools'
        ]
        
        for directory in directories:
            (output_path / directory).mkdir(exist_ok=True)
        
        # Create core course settings files
        self._create_canvas_export_txt(output_path / "course_settings" / "canvas_export.txt")
        self._create_course_settings_xml(output_path / "course_settings" / "course_settings.xml")
        self._create_context_xml(output_path / "course_settings" / "context.xml")
        self._create_assignment_groups_xml(output_path / "course_settings" / "assignment_groups.xml")
        self._create_files_meta_xml(output_path / "course_settings" / "files_meta.xml")
        self._create_late_policy_xml(output_path / "course_settings" / "late_policy.xml")
        self._create_media_tracks_xml(output_path / "course_settings" / "media_tracks.xml")
        
        # Module meta will be created later when modules are added
        self._create_empty_module_meta_xml(output_path / "course_settings" / "module_meta.xml")
        
        # Store output directory and update state
        self.output_dir = str(output_path)
        self._update_cartridge_state()
        
        return str(output_path)
    
    def _create_canvas_export_txt(self, filepath):
        """Create canvas_export.txt file"""
        content = "Q: What did the panda say when he was forced out of his natural habitat?\nA: This is un-BEAR-able\n"
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
    
    def _create_course_settings_xml(self, filepath):
        """Create course_settings.xml file"""
        content = f"""<?xml version="1.0" encoding="UTF-8"?>
<course identifier="{self.course_id}" xmlns="http://canvas.instructure.com/xsd/cccv1p0" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://canvas.instructure.com/xsd/cccv1p0 https://canvas.instructure.com/xsd/cccv1p0.xsd">
  <title>{self.course_title}</title>
  <course_code>{self.course_code}</course_code>
  <start_at/>
  <conclude_at/>
  <is_public>false</is_public>
  <allow_student_wiki_edits>false</allow_student_wiki_edits>
  <lock_all_announcements>false</lock_all_announcements>
  <allow_student_organized_groups>true</allow_student_organized_groups>
  <default_view>modules</default_view>
  <allow_final_grade_override>false</allow_final_grade_override>
  <usage_rights_required>false</usage_rights_required>
  <restrict_student_future_view>false</restrict_student_future_view>
  <restrict_student_past_view>false</restrict_student_past_view>
  <homeroom_course>false</homeroom_course>
  <horizon_course>false</horizon_course>
  <conditional_release>true</conditional_release>
  <content_library>false</content_library>
  <grading_standard_enabled>false</grading_standard_enabled>
  <storage_quota>500000000</storage_quota>
  <overridden_course_visibility/>
  <root_account_uuid>{self.root_account_uuid}</root_account_uuid>
  <default_post_policy>
    <post_manually>false</post_manually>
  </default_post_policy>
  <allow_final_grade_override>false</allow_final_grade_override>
  <enable_course_paces>false</enable_course_paces>
</course>
"""
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
    
    def _create_context_xml(self, filepath):
        """Create context.xml file"""
        course_id_num = abs(hash(self.course_id)) % 100000000
        content = f"""<?xml version="1.0" encoding="UTF-8"?>
<context_info xmlns="http://canvas.instructure.com/xsd/cccv1p0" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://canvas.instructure.com/xsd/cccv1p0 https://canvas.instructure.com/xsd/cccv1p0.xsd">
  <course_id>{course_id_num}</course_id>
  <course_name>{self.course_title}</course_name>
  <root_account_id>70000000000010</root_account_id>
  <root_account_name>Free for Teacher</root_account_name>
  <root_account_uuid>{self.root_account_uuid}</root_account_uuid>
  <canvas_domain>canvas.instructure.com</canvas_domain>
</context_info>
"""
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
    
    def _create_assignment_groups_xml(self, filepath):
        """Create assignment_groups.xml file"""
        content = f"""<?xml version="1.0" encoding="UTF-8"?>
<assignmentGroups xmlns="http://canvas.instructure.com/xsd/cccv1p0" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://canvas.instructure.com/xsd/cccv1p0 https://canvas.instructure.com/xsd/cccv1p0.xsd">
  <assignmentGroup identifier="{self.assignment_group_id}">
    <title>Assignments</title>
    <position>1</position>
    <group_weight>0.0</group_weight>
  </assignmentGroup>
</assignmentGroups>
"""
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
    
    def _create_files_meta_xml(self, filepath):
        """Create files_meta.xml file"""
        content = """<?xml version="1.0" encoding="UTF-8"?>
<fileMeta xmlns="http://canvas.instructure.com/xsd/cccv1p0" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://canvas.instructure.com/xsd/cccv1p0 https://canvas.instructure.com/xsd/cccv1p0.xsd">
</fileMeta>
"""
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
    
    def _create_late_policy_xml(self, filepath):
        """Create late_policy.xml file"""
        late_policy_id = f"g{uuid.uuid4().hex}"
        content = f"""<?xml version="1.0" encoding="UTF-8"?>
<late_policy identifier="{late_policy_id}" xmlns="http://canvas.instructure.com/xsd/cccv1p0" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://canvas.instructure.com/xsd/cccv1p0 https://canvas.instructure.com/xsd/cccv1p0.xsd">
  <missing_submission_deduction_enabled>false</missing_submission_deduction_enabled>
  <missing_submission_deduction>100.0</missing_submission_deduction>
  <late_submission_deduction_enabled>false</late_submission_deduction_enabled>
  <late_submission_deduction>0.0</late_submission_deduction>
  <late_submission_interval>day</late_submission_interval>
  <late_submission_minimum_percent_enabled>false</late_submission_minimum_percent_enabled>
  <late_submission_minimum_percent>0.0</late_submission_minimum_percent>
</late_policy>
"""
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
    
    def _create_media_tracks_xml(self, filepath):
        """Create media_tracks.xml file"""
        content = """<?xml version="1.0" encoding="UTF-8"?>
<media_tracks xmlns="http://canvas.instructure.com/xsd/cccv1p0" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://canvas.instructure.com/xsd/cccv1p0 https://canvas.instructure.com/xsd/cccv1p0.xsd">
</media_tracks>
"""
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
    
    def _create_empty_module_meta_xml(self, filepath):
        """Create empty module_meta.xml file"""
        content = """<?xml version="1.0" encoding="UTF-8"?>
<modules xmlns="http://canvas.instructure.com/xsd/cccv1p0" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://canvas.instructure.com/xsd/cccv1p0 https://canvas.instructure.com/xsd/cccv1p0.xsd">
</modules>
"""
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
    
    def add_module(self, module_title, position=None, published=True):
        """Add a module to the cartridge"""
        module_id = f"g{uuid.uuid4().hex}"
        
        module = {
            'identifier': module_id,
            'title': module_title,
            'position': position or len(self.modules) + 1,
            'workflow_state': 'published' if published else 'unpublished',
            'items': []
        }
        
        self.modules.append(module)
        
        # Add to organization structure
        self.organization_items.append({
            'identifier': module_id,
            'title': module_title,
            'type': 'module',
            'items': []
        })
        
        # Update cartridge state
        self._update_cartridge_state()
        
        return module_id
    
    
    
    def rename_module(self, module_id, new_title):
        """Rename a module by its identifier, keeping everything else the same"""
        # Find the module in our internal list
        module_to_rename = None
        for module in self.modules:
            if module['identifier'] == module_id:
                module_to_rename = module
                break
        
        if not module_to_rename:
            raise ValueError(f"Module with identifier {module_id} not found")
        
        # Store old title for comparison
        old_title = module_to_rename['title']
        
        # Check if title is actually changing
        if new_title == old_title:
            print(f"Module '{old_title}' (ID: {module_id}) - no change needed, title is already '{new_title}'")
            return True
        
        # Update the module title in the internal modules list
        module_to_rename['title'] = new_title
        
        # Update the module title in the organization items
        for org_module in self.organization_items:
            if org_module['identifier'] == module_id:
                org_module['title'] = new_title
                break
        
        # Update cartridge state to regenerate files
        self._update_cartridge_state()
        
        print(f"Module renamed: '{old_title}' → '{new_title}' (ID: {module_id})")
        return True
    
    
    
    
    
    
    def write_cartridge_files(self, output_dir):
        """Write all content files to the cartridge directory"""
        output_path = Path(output_dir)
        
        # Update module_meta.xml
        self._update_module_meta_xml(output_path / "course_settings" / "module_meta.xml")
        
        # Create wiki pages
        for page in self.wiki_pages:
            self._create_wiki_page_html(output_path / page['filename'], page)
        
        # Create assignments
        for assignment in self.assignments:
            self._create_assignment_files(output_path, assignment)
        
        # Create quizzes
        for quiz in self.quizzes:
            self._create_quiz_files(output_path, quiz)
        
        # Create announcements
        for announcement in self.announcements:
            self._create_announcement_files(output_path, announcement)
        
        # Create web resources
        for file_info in self.files:
            self._create_web_resource_file(output_path, file_info)
        
        # Create manifest
        self._create_imsmanifest_xml(output_path / "imsmanifest.xml")
        
        return str(output_path)
    
    def _update_module_meta_xml(self, filepath):
        """Update module_meta.xml with all modules"""
        content = """<?xml version="1.0" encoding="UTF-8"?>
<modules xmlns="http://canvas.instructure.com/xsd/cccv1p0" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://canvas.instructure.com/xsd/cccv1p0 https://canvas.instructure.com/xsd/cccv1p0.xsd">
"""
        
        for module in sorted(self.modules, key=lambda x: x.get('position', 1)):
            content += f"""  <module identifier="{module['identifier']}">
    <title>{module['title']}</title>
    <workflow_state>{module['workflow_state']}</workflow_state>
    <position>{module['position']}</position>
    <require_sequential_progress>false</require_sequential_progress>
    <locked>false</locked>
    <items>
"""
            
            for item in sorted(module['items'], key=lambda x: x.get('position', 1)):
                content_type = item.get('content_type', 'WikiPage')
                workflow_state = item.get('workflow_state', 'published')
                title = item.get('title', 'Untitled')
                identifierref = item.get('identifierref', '')
                position = item.get('position', 1)
                
                content += f"""      <item identifier="{item['identifier']}">
        <content_type>{content_type}</content_type>
        <workflow_state>{workflow_state}</workflow_state>
        <title>{title}</title>
        <identifierref>{identifierref}</identifierref>
        <position>{position}</position>
        <new_tab/>
        <indent>0</indent>
        <link_settings_json>null</link_settings_json>
      </item>
"""
            
            content += """    </items>
  </module>
"""
        
        content += "</modules>\n"
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
    
    def _create_wiki_page_html(self, filepath, page):
        """Create wiki page HTML file"""
        content = f"""<html>
<head>
<meta http-equiv="Content-Type" content="text/html; charset=utf-8"/>
<title>{page['title']}</title>
<meta name="identifier" content="{page['resource_id']}"/>
<meta name="editing_roles" content="teachers"/>
<meta name="workflow_state" content="{page['workflow_state']}"/>
</head>
<body>
{page['content']}
</body>
</html>"""
        
        filepath.parent.mkdir(parents=True, exist_ok=True)
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
    
    def _create_assignment_files(self, output_path, assignment):
        """Create assignment files"""
        assignment_dir = output_path / assignment['identifier']
        assignment_dir.mkdir(parents=True, exist_ok=True)
        
        # Create assignment_settings.xml
        settings_content = f"""<?xml version="1.0" encoding="UTF-8"?>
<assignment identifier="{assignment['identifier']}" xmlns="http://canvas.instructure.com/xsd/cccv1p0" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://canvas.instructure.com/xsd/cccv1p0 https://canvas.instructure.com/xsd/cccv1p0.xsd">
  <title>{assignment['title']}</title>
  <due_at/>
  <lock_at/>
  <unlock_at/>
  <module_locked>false</module_locked>
  <assignment_group_identifierref>{assignment['assignment_group_id']}</assignment_group_identifierref>
  <workflow_state>{assignment['workflow_state']}</workflow_state>
  <assignment_overrides>
  </assignment_overrides>
  <allowed_extensions></allowed_extensions>
  <has_group_category>false</has_group_category>
  <points_possible>{assignment['points_possible']}.0</points_possible>
  <grading_type>points</grading_type>
  <all_day>false</all_day>
  <submission_types>on_paper</submission_types>
  <position>{assignment['position']}</position>
  <turnitin_enabled>false</turnitin_enabled>
  <vericite_enabled>false</vericite_enabled>
  <peer_review_count>0</peer_review_count>
  <peer_reviews>false</peer_reviews>
  <automatic_peer_reviews>false</automatic_peer_reviews>
  <anonymous_peer_reviews>false</anonymous_peer_reviews>
  <grade_group_students_individually>false</grade_group_students_individually>
  <freeze_on_copy>false</freeze_on_copy>
  <omit_from_final_grade>false</omit_from_final_grade>
  <hide_in_gradebook>false</hide_in_gradebook>
  <intra_group_peer_reviews>false</intra_group_peer_reviews>
  <only_visible_to_overrides>false</only_visible_to_overrides>
  <post_to_sis>false</post_to_sis>
  <moderated_grading>false</moderated_grading>
  <grader_count>0</grader_count>
  <grader_comments_visible_to_graders>true</grader_comments_visible_to_graders>
  <anonymous_grading>false</anonymous_grading>
  <graders_anonymous_to_graders>false</graders_anonymous_to_graders>
  <grader_names_visible_to_final_grader>true</grader_names_visible_to_final_grader>
  <anonymous_instructor_annotations>false</anonymous_instructor_annotations>
  <post_policy>
    <post_manually>false</post_manually>
  </post_policy>
</assignment>
"""
        
        with open(assignment_dir / "assignment_settings.xml", 'w', encoding='utf-8') as f:
            f.write(settings_content)
        
        # Create assignment content HTML
        html_content = f"""<html>
<head>
<meta http-equiv="Content-Type" content="text/html; charset=utf-8"/>
<title>Assignment: {assignment['title']}</title>
</head>
<body>
<p>{assignment['content']}</p>
</body>
</html>"""
        
        with open(assignment_dir / "my-first-assignment.html", 'w', encoding='utf-8') as f:
            f.write(html_content)
    
    def _create_quiz_files(self, output_path, quiz):
        """Create quiz files"""
        quiz_dir = output_path / quiz['identifier']
        quiz_dir.mkdir(parents=True, exist_ok=True)
        
        # Store QTI file IDs for this quiz to track them for deletion
        if not hasattr(self, 'quiz_qti_files'):
            self.quiz_qti_files = {}
        
        # Create assessment_meta.xml
        meta_content = f"""<?xml version="1.0" encoding="UTF-8"?>
<quiz identifier="{quiz['identifier']}" xmlns="http://canvas.instructure.com/xsd/cccv1p0" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://canvas.instructure.com/xsd/cccv1p0 https://canvas.instructure.com/xsd/cccv1p0.xsd">
  <title>{quiz['title']}</title>
  <description>&lt;p&gt;{quiz['description']}&lt;/p&gt;</description>
  <shuffle_answers>false</shuffle_answers>
  <scoring_policy>keep_highest</scoring_policy>
  <hide_results>always</hide_results>
  <quiz_type>assignment</quiz_type>
  <points_possible>{quiz['points_possible']}.0</points_possible>
  <require_lockdown_browser>false</require_lockdown_browser>
  <require_lockdown_browser_for_results>false</require_lockdown_browser_for_results>
  <require_lockdown_browser_monitor>false</require_lockdown_browser_monitor>
  <lockdown_browser_monitor_data/>
  <show_correct_answers>false</show_correct_answers>
  <anonymous_submissions>false</anonymous_submissions>
  <could_be_locked>false</could_be_locked>
  <disable_timer_autosubmission>false</disable_timer_autosubmission>
  <allowed_attempts>1</allowed_attempts>
  <one_question_at_a_time>false</one_question_at_a_time>
  <cant_go_back>false</cant_go_back>
  <available>true</available>
  <one_time_results>false</one_time_results>
  <show_correct_answers_last_attempt>false</show_correct_answers_last_attempt>
  <only_visible_to_overrides>false</only_visible_to_overrides>
  <module_locked>false</module_locked>
  <assignment identifier="{quiz['assignment_id']}">
    <title>{quiz['title']}</title>
    <due_at/>
    <lock_at/>
    <unlock_at/>
    <module_locked>false</module_locked>
    <assignment_group_identifierref>{quiz['assignment_group_id']}</assignment_group_identifierref>
    <workflow_state>{quiz['workflow_state']}</workflow_state>
    <assignment_overrides>
    </assignment_overrides>
    <quiz_identifierref>{quiz['identifier']}</quiz_identifierref>
    <allowed_extensions></allowed_extensions>
    <has_group_category>false</has_group_category>
    <points_possible>{quiz['points_possible']}.0</points_possible>
    <grading_type>points</grading_type>
    <all_day>false</all_day>
    <submission_types>online_quiz</submission_types>
    <position>{quiz['position']}</position>
    <turnitin_enabled>false</turnitin_enabled>
    <vericite_enabled>false</vericite_enabled>
    <peer_review_count>0</peer_review_count>
    <peer_reviews>false</peer_reviews>
    <automatic_peer_reviews>false</automatic_peer_reviews>
    <anonymous_peer_reviews>false</anonymous_peer_reviews>
    <grade_group_students_individually>false</grade_group_students_individually>
    <freeze_on_copy>false</freeze_on_copy>
    <omit_from_final_grade>false</omit_from_final_grade>
    <hide_in_gradebook>false</hide_in_gradebook>
    <intra_group_peer_reviews>false</intra_group_peer_reviews>
    <only_visible_to_overrides>false</only_visible_to_overrides>
    <post_to_sis>false</post_to_sis>
    <moderated_grading>false</moderated_grading>
    <grader_count>0</grader_count>
    <grader_comments_visible_to_graders>true</grader_comments_visible_to_graders>
    <anonymous_grading>false</anonymous_grading>
    <graders_anonymous_to_graders>false</graders_anonymous_to_graders>
    <grader_names_visible_to_final_grader>true</grader_names_visible_to_final_grader>
    <anonymous_instructor_annotations>false</anonymous_instructor_annotations>
    <post_policy>
      <post_manually>false</post_manually>
    </post_policy>
  </assignment>
  <assignment_group_identifierref>{quiz['assignment_group_id']}</assignment_group_identifierref>
  <assignment_overrides>
  </assignment_overrides>
</quiz>
"""
        
        with open(quiz_dir / "assessment_meta.xml", 'w', encoding='utf-8') as f:
            f.write(meta_content)
        
        # Create assessment_qti.xml
        qti_content = f"""<?xml version="1.0" encoding="UTF-8"?>
<questestinterop xmlns="http://www.imsglobal.org/xsd/ims_qtiasiv1p2" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://www.imsglobal.org/xsd/ims_qtiasiv1p2 http://www.imsglobal.org/xsd/ims_qtiasiv1p2p1.xsd">
  <assessment ident="{quiz['identifier']}" title="{quiz['title']}">
    <qtimetadata>
      <qtimetadatafield>
        <fieldlabel>cc_maxattempts</fieldlabel>
        <fieldentry>1</fieldentry>
      </qtimetadatafield>
    </qtimetadata>
    <section ident="root_section">
      <item ident="{quiz['question_id']}" title="Question">
        <itemmetadata>
          <qtimetadata>
            <qtimetadatafield>
              <fieldlabel>question_type</fieldlabel>
              <fieldentry>multiple_choice_question</fieldentry>
            </qtimetadatafield>
            <qtimetadatafield>
              <fieldlabel>points_possible</fieldlabel>
              <fieldentry>{quiz['points_possible']}.0</fieldentry>
            </qtimetadatafield>
            <qtimetadatafield>
              <fieldlabel>original_answer_ids</fieldlabel>
              <fieldentry>5666,7024,7959,520</fieldentry>
            </qtimetadatafield>
            <qtimetadatafield>
              <fieldlabel>assessment_question_identifierref</fieldlabel>
              <fieldentry>{quiz['assessment_question_id']}</fieldentry>
            </qtimetadatafield>
          </qtimetadata>
        </itemmetadata>
        <presentation>
          <material>
            <mattext texttype="text/html">&lt;div&gt;&lt;p&gt;Sample question: What is 2 + 2?&lt;/p&gt;&lt;/div&gt;</mattext>
          </material>
          <response_lid ident="response1" rcardinality="Single">
            <render_choice>
              <response_label ident="5666">
                <material>
                  <mattext texttype="text/plain">3</mattext>
                </material>
              </response_label>
              <response_label ident="7024">
                <material>
                  <mattext texttype="text/plain">4</mattext>
                </material>
              </response_label>
              <response_label ident="7959">
                <material>
                  <mattext texttype="text/plain">5</mattext>
                </material>
              </response_label>
              <response_label ident="520">
                <material>
                  <mattext texttype="text/plain">6</mattext>
                </material>
              </response_label>
            </render_choice>
          </response_lid>
        </presentation>
        <resprocessing>
          <outcomes>
            <decvar maxvalue="100" minvalue="0" varname="SCORE" vartype="Decimal"/>
          </outcomes>
          <respcondition continue="No">
            <conditionvar>
              <varequal respident="response1">7024</varequal>
            </conditionvar>
            <setvar action="Set" varname="SCORE">100</setvar>
          </respcondition>
        </resprocessing>
      </item>
    </section>
  </assessment>
</questestinterop>
"""
        
        with open(quiz_dir / "assessment_qti.xml", 'w', encoding='utf-8') as f:
            f.write(qti_content)
        
        # Create QTI file in non_cc_assessments - only create one file per quiz
        qti_path = output_path / "non_cc_assessments" / f"{quiz['identifier']}.xml.qti"
        qti_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(qti_path, 'w', encoding='utf-8') as f:
            f.write(qti_content)
        
        # Track QTI files for this quiz (only one now)
        self.quiz_qti_files[quiz['identifier']] = [f"{quiz['identifier']}.xml.qti"]
    
    def _create_announcement_files(self, output_path, announcement):
        """Create announcement and discussion topic files"""
        # Determine file paths based on resource href
        topic_file_path = None
        meta_file_path = None
        
        # Check if this is a standalone discussion (files in root) or module discussion (files in discussions/)
        for resource in self.resources:
            if resource['identifier'] == announcement['topic_id']:
                if resource['href'].startswith('discussions/'):
                    # Module discussion - files in discussions/ subdirectory
                    topic_file_path = output_path / resource['href']
                else:
                    # Standalone discussion - files in root directory
                    topic_file_path = output_path / resource['href']
                break
        
        for resource in self.resources:
            if resource['identifier'] == announcement['meta_id']:
                if resource['href'].startswith('discussions/'):
                    # Module discussion - files in discussions/ subdirectory
                    meta_file_path = output_path / resource['href']
                else:
                    # Standalone discussion - files in root directory
                    meta_file_path = output_path / resource['href']
                break
        
        # Create announcement topic XML (topic content)
        # Get the content and properly escape it for XML
        content = announcement.get('content', announcement.get('body', ''))
        
        # If content doesn't already contain HTML tags, wrap it in <p> tags
        import html
        if content and not ('<' in content and '>' in content):
            # Plain text content - wrap in paragraph tags and escape
            escaped_content = html.escape(f'<p>{content}</p>')
        elif content:
            # Content already has HTML tags - just escape it
            escaped_content = html.escape(content)
        else:
            # Empty content
            escaped_content = html.escape('<p></p>')
        
        topic_content = f"""<?xml version="1.0" encoding="UTF-8"?>
<topic xmlns="http://www.imsglobal.org/xsd/imsccv1p1/imsdt_v1p1" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://www.imsglobal.org/xsd/imsccv1p1/imsdt_v1p1  http://www.imsglobal.org/profile/cc/ccv1p1/ccv1p1_imsdt_v1p1.xsd">
  <title>{announcement['title']}</title>
  <text texttype="text/html">{escaped_content}</text>
</topic>
"""
        
        # Ensure directory exists and write topic file
        if topic_file_path:
            topic_file_path.parent.mkdir(parents=True, exist_ok=True)
            with open(topic_file_path, 'w', encoding='utf-8') as f:
                f.write(topic_content)
        
        # Create announcement meta XML (topicMeta)
        meta_content = f"""<?xml version="1.0" encoding="UTF-8"?>
<topicMeta identifier="{announcement['meta_id']}" xmlns="http://canvas.instructure.com/xsd/cccv1p0" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://canvas.instructure.com/xsd/cccv1p0 https://canvas.instructure.com/xsd/cccv1p0.xsd">
  <topic_id>{announcement['topic_id']}</topic_id>
  <title>{announcement['title']}</title>
  <position>{announcement.get('position', '')}</position>
  <type>{'topic' if 'body' in announcement else 'announcement'}</type>
  <discussion_type>threaded</discussion_type>
  <has_group_category>false</has_group_category>
  <workflow_state>{announcement['workflow_state']}</workflow_state>
  <module_locked>false</module_locked>
  <allow_rating>false</allow_rating>
  <only_graders_can_rate>false</only_graders_can_rate>
  <sort_by_rating>false</sort_by_rating>
  <sort_order>{'asc' if 'body' not in announcement else 'desc'}</sort_order>
  <sort_order_locked>false</sort_order_locked>
  <expanded>{'true' if 'body' not in announcement else 'false'}</expanded>
  <expanded_locked>false</expanded_locked>
  <todo_date/>
  <locked>{'true' if 'body' not in announcement else 'false'}</locked>
</topicMeta>
"""
        
        # Ensure directory exists and write meta file
        if meta_file_path:
            meta_file_path.parent.mkdir(parents=True, exist_ok=True)
            with open(meta_file_path, 'w', encoding='utf-8') as f:
                f.write(meta_content)
    
    def _create_web_resource_file(self, output_path, file_info):
        """Create web resource file"""
        file_path = output_path / file_info['path']
        file_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(file_info['content'])
    
    def _create_imsmanifest_xml(self, filepath):
        """Create imsmanifest.xml file"""
        today = datetime.now().strftime("%Y-%m-%d")
        
        content = f"""<?xml version="1.0" encoding="UTF-8"?>
<manifest identifier="{self.manifest_id}" xmlns="http://www.imsglobal.org/xsd/imsccv1p1/imscp_v1p1" xmlns:lom="http://ltsc.ieee.org/xsd/imsccv1p1/LOM/resource" xmlns:lomimscc="http://ltsc.ieee.org/xsd/imsccv1p1/LOM/manifest" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://www.imsglobal.org/xsd/imsccv1p1/imscp_v1p1 http://www.imsglobal.org/profile/cc/ccv1p1/ccv1p1_imscp_v1p2_v1p0.xsd http://ltsc.ieee.org/xsd/imsccv1p1/LOM/resource http://www.imsglobal.org/profile/cc/ccv1p1/LOM/ccv1p1_lomresource_v1p0.xsd http://ltsc.ieee.org/xsd/imsccv1p1/LOM/manifest http://www.imsglobal.org/profile/cc/ccv1p1/LOM/ccv1p1_lommanifest_v1p0.xsd">
  <metadata>
    <schema>IMS Common Cartridge</schema>
    <schemaversion>1.1.0</schemaversion>
    <lomimscc:lom>
      <lomimscc:general>
        <lomimscc:title>
          <lomimscc:string>{self.course_title}</lomimscc:string>
        </lomimscc:title>
      </lomimscc:general>
      <lomimscc:lifeCycle>
        <lomimscc:contribute>
          <lomimscc:date>
            <lomimscc:dateTime>{today}</lomimscc:dateTime>
          </lomimscc:date>
        </lomimscc:contribute>
      </lomimscc:lifeCycle>
      <lomimscc:rights>
        <lomimscc:copyrightAndOtherRestrictions>
          <lomimscc:value>yes</lomimscc:value>
        </lomimscc:copyrightAndOtherRestrictions>
        <lomimscc:description>
          <lomimscc:string>Private (Copyrighted) - http://en.wikipedia.org/wiki/Copyright</lomimscc:string>
        </lomimscc:description>
      </lomimscc:rights>
    </lomimscc:lom>
  </metadata>
  <organizations>
    <organization identifier="org_1" structure="rooted-hierarchy">
      <item identifier="LearningModules">
"""
        
        # Add unique organization items (modules), sorted by position
        seen_org_items = set()
        
        # Sort organization items by their corresponding module positions
        def get_module_position(org_item):
            # Find the corresponding module to get its position
            for module in self.modules:
                if module['identifier'] == org_item['identifier']:
                    return module.get('position', 1)
            return 1  # Default position if not found
        
        sorted_org_items = sorted(self.organization_items, key=get_module_position)
        
        for org_item in sorted_org_items:
            if org_item['identifier'] not in seen_org_items:
                seen_org_items.add(org_item['identifier'])
                content += f"""        <item identifier="{org_item['identifier']}">
          <title>{org_item['title']}</title>
"""
                # Add unique items within this module
                seen_items = set()
                for item in sorted(org_item['items'], key=lambda x: x.get('position', 1)):
                    item_key = (item['identifier'], item.get('identifierref', ''))
                    if item_key not in seen_items:
                        seen_items.add(item_key)
                        content += f"""          <item identifier="{item['identifier']}" identifierref="{item.get('identifierref', '')}">
            <title>{item.get('title', 'Untitled')}</title>
          </item>
"""
                content += """        </item>
"""
        
        content += """      </item>
    </organization>
  </organizations>
  <resources>
"""
        
        # Add unique resources (avoid duplicates)
        seen_resources = set()
        
        # Add course settings resource first
        course_settings_key = (self.course_id, "associatedcontent/imscc_xmlv1p1/learning-application-resource", "course_settings/canvas_export.txt")
        seen_resources.add(course_settings_key)
        content += f"""    <resource identifier="{self.course_id}" type="associatedcontent/imscc_xmlv1p1/learning-application-resource" href="course_settings/canvas_export.txt">
      <file href="course_settings/course_settings.xml"/>
      <file href="course_settings/module_meta.xml"/>
      <file href="course_settings/assignment_groups.xml"/>
      <file href="course_settings/files_meta.xml"/>
      <file href="course_settings/late_policy.xml"/>
      <file href="course_settings/context.xml"/>
      <file href="course_settings/media_tracks.xml"/>
      <file href="course_settings/canvas_export.txt"/>
    </resource>
"""
        
        for resource in self.resources:
            resource_key = (resource['identifier'], resource['type'], resource['href'])
            if resource_key not in seen_resources:
                seen_resources.add(resource_key)
                content += f"""    <resource identifier="{resource['identifier']}" type="{resource['type']}" href="{resource['href']}">
      <file href="{resource['href']}"/>
"""
                
                # Add assignment settings files
                if resource['type'] == 'associatedcontent/imscc_xmlv1p1/learning-application-resource' and resource['href'].endswith('.html'):
                    assignment_id = resource['href'].split('/')[0]
                    content += f"""      <file href="{assignment_id}/assignment_settings.xml"/>
"""
                
                # Add quiz dependency files
                if resource['type'] == 'imsqti_xmlv1p2/imscc_xmlv1p1/assessment':
                    quiz_id = resource['href'].split('/')[0]
                    content += f"""      <dependency identifierref="{resource['dependency']}"/>
"""
                
                # Add assessment meta files
                if resource['type'] == 'associatedcontent/imscc_xmlv1p1/learning-application-resource' and 'assessment_meta.xml' in resource['href']:
                    quiz_id = resource['href'].split('/')[0]
                    content += f"""      <file href="non_cc_assessments/{quiz_id}.xml.qti"/>
"""
                
                # Add announcement dependencies
                if resource['type'] == 'imsdt_xmlv1p1' and 'dependency' in resource:
                    content += f"""      <dependency identifierref="{resource['dependency']}"/>
"""
                
                content += """    </resource>
"""
        
        content += """  </resources>
</manifest>
"""
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)


def count_files_and_lines(directory):
    """Count files and lines in a directory"""
    file_count = 0
    line_count = 0
    
    for file_path in Path(directory).rglob("*"):
        if file_path.is_file():
            file_count += 1
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    line_count += len(f.readlines())
            except UnicodeDecodeError:
                # Handle binary files
                line_count += 1
    
    return file_count, line_count
