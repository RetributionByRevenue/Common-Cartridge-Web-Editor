import uuid


class CartridgeStandaloneAddMixin:
    """
    Mixin class containing standalone add methods for CartridgeGenerator.
    This mixin provides methods to add various content types as standalone items 
    (not attached to any specific module).
    """

    def add_assignment_standalone(self, assignment_title, assignment_content="", points=100, published=True):
        """Add an assignment to the cartridge"""
        assignment_id = f"g{uuid.uuid4().hex}"
        
        assignment = {
            'identifier': assignment_id,
            'title': assignment_title,
            'content': assignment_content,
            'points_possible': points,
            'workflow_state': 'published' if published else 'unpublished',
            'assignment_group_id': self.assignment_group_id,
            'position': len(self.assignments) + 1
        }
        
        self.assignments.append(assignment)
        
        # Add to resources
        self.resources.append({
            'identifier': assignment_id,
            'type': 'associatedcontent/imscc_xmlv1p1/learning-application-resource',
            'href': f"{assignment_id}/my-first-assignment.html"
        })
        
        # Update cartridge state
        self._update_cartridge_state()
        
        return assignment_id

    def add_quiz_standalone(self, quiz_title, quiz_description="", points=1, published=True):
        """Add a quiz to the cartridge"""
        quiz_id = f"g{uuid.uuid4().hex}"
        assignment_id = f"g{uuid.uuid4().hex}"
        resource_id = f"g{uuid.uuid4().hex}"
        question_id = f"g{uuid.uuid4().hex}"
        assessment_question_id = f"g{uuid.uuid4().hex}"
        
        quiz = {
            'identifier': quiz_id,
            'title': quiz_title,
            'description': quiz_description,
            'points_possible': points,
            'workflow_state': 'published' if published else 'unpublished',
            'assignment_id': assignment_id,
            'assignment_group_id': self.assignment_group_id,
            'position': len(self.quizzes) + 1,
            'question_id': question_id,
            'assessment_question_id': assessment_question_id
        }
        
        self.quizzes.append(quiz)
        
        # Add to resources
        self.resources.append({
            'identifier': quiz_id,
            'type': 'imsqti_xmlv1p2/imscc_xmlv1p1/assessment',
            'href': f"{quiz_id}/assessment_qti.xml",
            'dependency': resource_id
        })
        
        self.resources.append({
            'identifier': resource_id,
            'type': 'associatedcontent/imscc_xmlv1p1/learning-application-resource',
            'href': f"{quiz_id}/assessment_meta.xml"
        })
        
        # Update cartridge state
        self._update_cartridge_state()
        
        return quiz_id

    def add_wiki_page_standalone(self, page_title, page_content="", published=True):
        """Add a standalone wiki page (not attached to any module)"""
        page_id = f"g{uuid.uuid4().hex}"
        resource_id = f"g{uuid.uuid4().hex}"
        
        # Store wiki page info
        wiki_page = {
            'identifier': page_id,
            'resource_id': resource_id,
            'title': page_title,
            'content': page_content,
            'workflow_state': 'published' if published else 'unpublished',
            'filename': f"wiki_content/{page_title.lower().replace(' ', '-').replace('_', '-')}.html"
        }
        self.wiki_pages.append(wiki_page)
        
        # Add to resources (but not to organization structure)
        self.resources.append({
            'identifier': resource_id,
            'type': 'webcontent',
            'href': wiki_page['filename']
        })
        
        # Update cartridge state
        self._update_cartridge_state()
        
        return page_id

    def add_discussion_standalone(self, title, body, published=True):
        """Add a standalone discussion (not attached to any module)"""
        topic_id = f"g{uuid.uuid4().hex}"
        meta_id = f"g{uuid.uuid4().hex}"
        
        # Store discussion topic info
        discussion_topic = {
            'topic_id': topic_id,
            'meta_id': meta_id,
            'title': title,
            'body': body,
            'workflow_state': 'unpublished' if not published else 'active',
        }
        self.announcements.append(discussion_topic)
        
        # Add to resources (files go in root directory, not discussions/ subdirectory)
        self.resources.append({
            'identifier': topic_id,
            'type': 'imsdt_xmlv1p1',
            'href': f"{topic_id}.xml",
            'dependency': meta_id
        })
        
        self.resources.append({
            'identifier': meta_id,
            'type': 'associatedcontent/imscc_xmlv1p1/learning-application-resource',
            'href': f"{meta_id}.xml"
        })
        
        # Update cartridge state
        self._update_cartridge_state()
        
        return topic_id

    def add_file_standalone(self, filename, file_content):
        """Add a standalone file (not attached to any module)"""
        file_id = f"g{uuid.uuid4().hex}"
        
        # Store file info
        file_info = {
            'identifier': file_id,
            'filename': filename,
            'content': file_content,
            'path': f"web_resources/{filename}"
        }
        self.files.append(file_info)
        
        # Add to resources (files go in web_resources/ directory)
        self.resources.append({
            'identifier': file_id,
            'type': 'webcontent',
            'href': f"web_resources/{filename}"
        })
        
        # Update cartridge state
        self._update_cartridge_state()
        
        return file_id