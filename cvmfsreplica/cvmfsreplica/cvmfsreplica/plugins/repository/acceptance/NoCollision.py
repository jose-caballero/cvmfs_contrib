#!/usr/bin/env python

import datetime
import logging
import os
import time

from cvmfsreplica.cvmfsreplicaex import PluginConfigurationFailure, AcceptancePluginFailed
from cvmfsreplica.interfaces import RepositoryPluginAcceptanceInterface
from cvmfsreplica.utils import check_disk_space
import cvmfsreplica.pluginsmanagement as pm


class NoCollision(RepositoryPluginAcceptanceInterface):

    def __init__(self, repository, conf):
        self.log = logging.getLogger('cvmfsreplica.nocollision')
        self.repository = repository
        self.repositoryname = self.conf.get('repositoryname')
        self.conf = conf
        try:
           self.timeout = self.conf.getint('nocollision.timeout')
           self.reportplugins = pm.readplugins(self.repository, 
                                               'repository', 
                                               'report', 
                                               self.conf.namespace('acceptance.nocollision.', 
                                                                   exclude=True)
                                               )
        except:
           raise PluginConfigurationFailure('failed to initialize Diskspace plugin')
        try:
            self.should_abort = self.conf.getboolean('diskspace.should_abort')
        except:
            self.should_abort = True #Default

        self.log.debug('plugin Diskspace initialized properly')


    def verify(self):
        '''
        checks if we are not already replicating this repo
        '''

        try:
            return self._check_no_collision()
        except Exception, ex:
            raise ex


    def _check_no_collision(self):

        replicating = True
        inittime  = datetime.datetime.now()
        delta = 0

        while delta < self.timeout and replicating == True:

            path = "/var/spool/cvmfs/%s/is_updating.lock" %self.repositoryname
            replicating = os.path.isfile(path)
            if replicating:
                interval = self.conf.getint('interval')
                time.sleep(interval) 
            now = datetime.datetime.now()     
            delta = (now - inittime).seconds

        # the while loop finished...
        # let's check why 
        if replicating == False:
            # we are not replicating this repo, so we can proceed
            return True
        else:
            # the loop finished because timeout
            msg = 'The repository %s is already being replicating, and waiting loop for %s seconds timed out' %(self.repositoryname, self.timeout)
            self._notify_failure(msg)
            self.log.error(msg)
            if self.should_abort:
                self.log.error('Raising exception')
                raise AcceptancePluginFailed(msg)
            else:
                return False

    
    def _notify_failure(self, msg):
        for report in self.reportplugins:
            report.notifyfailure(msg)

        

