# -*- coding: utf-8 -*-
import os
from core.toad.generictask import GenericTask
from lib import mriutil, util
from lib.images import Images


class Tractometry(GenericTask):
    def __init__(self, subject):
        GenericTask.__init__(
            self, subject, 'tensorfsl', 'tensormrtrix', 'tensordipy',
            'tractfiltering', 'qa')
        self.setCleanupBeforeImplement(False)
        self.dirty = True


    def implement(self):
        pass
        mriutil.setWorkingDirTractometry(self.workingDir,
                                         None,
                                         self.__buildListMetrics())

        #mriutil.runTractometry(configTractometry, filteredTractographies, self.workingDir)


    def __buildListMetrics(self):
        return [(self.getTensorFSLImage('dwi', 'fa'),'fsl_fa.nii.gz'),
                (self.getTensorFSLImage('dwi', 'md'),'fsl_md.nii.gz'),
                (self.getTensorFSLImage('dwi', 'ad'),'fsl_ad.nii.gz'),
                (self.getTensorFSLImage('dwi', 'md'),'fsl_rd.nii.gz'),
                (self.getTensorDIPYImage('dwi', 'fa'),'dipy_fa.nii.gz'),
                (self.getTensorDIPYImage('dwi', 'md'),'dipy_md.nii.gz'),
                (self.getTensorDIPYImage('dwi', 'ad'),'dipy_ad.nii.gz'),
                (self.getTensorDIPYImage('dwi', 'md'),'dipy_rd.nii.gz'),
                (self.getTensorMRTRIXImage('dwi', 'fa'),'mrtrix_fa.nii.gz'),
                (self.getTensorMRTRIXImage('dwi', 'md'),'mrtrix_md.nii.gz'),
                (self.getTensorMRTRIXImage('dwi', 'ad'),'mrtrix_ad.nii.gz'),
                (self.getTensorMRTRIXImage('dwi', 'md'),'mrtrix_rd.nii.gz')]


    def isIgnore(self):
        return self.get("ignore")


    def meetRequirement(self):
        """Validate if all requirements have been met prior to launch the task
        Returns:
            True if all requirement are meet, False otherwise
        """

        images = Images()

        return True


    def isDirty(self):
        """Validate if this tasks need to be submit during the execution
        Returns:
            True if any expected file or resource is missing, False otherwise
        """

        return True


#    def qaSupplier(self):
#        """Create and supply images for the report generated by qa task
#
#        """
#        qaImages = Images()
#
#        return qaImages
