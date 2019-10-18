#!/usr/bin/env python

import logging
import os
import subprocess 
import time

from cvmfsreplica.cvmfsreplicaex import PluginConfigurationFailure
from cvmfsreplica.interfaces import RepositoryPluginPostInterface



class Delay(RepositoryPluginPostInterface):

    def __init__(self, repository, conf):
        self.log = logging.getLogger('cvmfsreplica.delay')
        self.repository = repository
        self.conf = conf
        self.time = self.conf.getint('delay.time')
        self.log.debug('plugin Delay initialized properly')

    def run(self):
        self.log.debug('about to sleep for %s seconds' %self.time)
        time.sleep(self.time)
        self.log.debug('done sleeping')


