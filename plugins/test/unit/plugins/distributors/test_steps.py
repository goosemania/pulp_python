import os
import shutil
import tempfile
import unittest

from mock import Mock, patch

from pulp.plugins.model import Repository
from pulp.plugins.config import PluginCallConfiguration
from pulp.plugins.conduits.repo_publish import RepoPublishConduit

from pulp_python.common import constants
from pulp_python.plugins.distributors import steps


class TestWebPublisher(unittest.TestCase):

    def setUp(self):
        self.working_directory = tempfile.mkdtemp()
        self.publish_dir = os.path.join(self.working_directory, 'publish')
        self.repo_working = os.path.join(self.working_directory, 'work')

        self.repo = Mock(id='foo', working_dir=self.repo_working)
        self.config = PluginCallConfiguration({constants.CONFIG_KEY_PUBLISH_DIRECTORY:
                                              self.publish_dir}, {})

    def tearDown(self):
        shutil.rmtree(self.working_directory)

    @patch('pulp_python.plugins.distributors.steps.AtomicDirectoryPublishStep')
    @patch('pulp_python.plugins.distributors.steps.PublishContentStep')
    @patch('pulp_python.plugins.distributors.steps.PublishMetadataStep')
    def test_init(self, mock_metadata, mock_content, mock_atomic):
        mock_conduit = Mock()
        mock_config = {
            constants.CONFIG_KEY_PUBLISH_DIRECTORY: self.publish_dir
        }
        publisher = steps.PythonPublisher(self.repo, mock_conduit, mock_config)
        self.assertEquals(publisher.children, [mock_metadata.return_value,
                                               mock_content.return_value,
                                               mock_atomic.return_value])


class TestPublishContentStep(unittest.TestCase):

    def setUp(self):
        self.working_directory = tempfile.mkdtemp()
        self.publish_dir = os.path.join(self.working_directory, 'publish')
        self.working_temp = os.path.join(self.working_directory, 'work')
        self.repo = Mock(id='foo', working_dir=self.working_temp)

    def tearDown(self):
        shutil.rmtree(self.working_directory)

    def test_process_main(self):
        step = steps.PublishContentStep()
        step.process_main()


class TestPublishMetadataStep(unittest.TestCase):

    def setUp(self):
        self.working_directory = tempfile.mkdtemp()
        self.publish_dir = os.path.join(self.working_directory, 'publish')
        self.working_temp = os.path.join(self.working_directory, 'work')
        os.makedirs(self.working_temp)
        self.repo = Repository(id='foo', working_dir=self.working_temp)
        config = PluginCallConfiguration(None, None)
        conduit = RepoPublishConduit(self.repo.id, 'foo_repo')
        conduit.get_repo_scratchpad = Mock(return_value={u'tags': {}})
        self.parent = steps.PluginStep('test-step', self.repo, conduit, config)

    def tearDown(self):
        shutil.rmtree(self.working_directory)