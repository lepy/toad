# -*- coding: utf-8 -*-


import csv
import os
from core.toad.generictask import GenericTask
from lib import mriutil, util
from lib.images import Images


class Tractometry(GenericTask):

    def __init__(self, subject):
        GenericTask.__init__(
                self, subject, 'preparation', 'tensorfsl', 'tensormrtrix',
                'tensordipy', 'hardimrtrix', 'hardidipy', 'tractfiltering',)
        self.setCleanupBeforeImplement(False)

        self.absInDir = os.path.join(self.workingDir, 'input')
        self.absOutDir = os.path.join(self.workingDir, 'output')

    def implement(self):
        mriutil.setWorkingDirTractometry(
                self.workingDir,
                self.getTractFilteringImages('dwi', None, 'trk','input/subject/bundles/'),
                self.__buildListMetrics()
                )

        configFile = self.__getConfigFile(
                'configTractometry', 'configTractometry_default')

        cmdTpl = "scil_run_tractometry.py --config_file {0} {1} {2} -v -f "
        cmd = cmdTpl.format(configFile, self.absInDir, self.absOutDir)
        self.launchCommand(cmd)

        csvToClean = [
                ('count.csv', 'simple'),
                ('volume.csv', 'simple'),
                ('mean.csv', 'simple'),
                ('mean_perpoint.csv', 'simple'),
                ('profile_mean.csv', 'simple'),
                ('profile_std.csv', 'simple'),
                ('std.csv', 'simple'),
                ('std_perpoint.csv', 'simple'),
                ]
        for csvPath, method in csvToClean:
            if os.path.isfile(self.absOutDir+csvPath):
                self.cleanCsv(self.absOutDir+csvPath, method)


    def cleanCsv(self, csvPath, method):
        # Build out path
        csvOut = self.buildName(csvPath, 'cleaned', '.csv')

        # Load csv
        with open(csvPath, 'rb') as f:
            reader = csv.reader(f)
            data = list(reader)

        # Clean data
        if method == 'simple':
            outData = [['subject'],[self.subject]]
            firstRow = data[0][1:]
            commonprefix = os.path.commonprefix(firstRow)
            outData[0] += [s.replace(commonprefix,'') for s in firstRow]
            outData[1] += data[1][1:]

        elif method == 'metric':
            #TODO implement when csv are per metric
            pass

        elif method == 'profile':
            #TODO implement when csv are per profile
            pass

        # Save csv
        with open(csvOut, 'wb') as f:
            writer = csv.writer(f)
            writer.writerows(outData)


    def isIgnore(self):
        return self.get("ignore")


    def meetRequirement(self):
        """Validate if all requirements have been met prior to launch the task
        Returns:
            True if all requirement are meet, False otherwise
        """
        return os.path.isdir(os.path.join(
                self.tractfilteringDir, 'output', 'subject', 'outlier_cleaned_tracts'))


    def isDirty(self):
        """Validate if this tasks need to be submit during the execution
        Returns:
            True if any expected file or resource is missing, False otherwise
        """
        return not os.path.isdir(os.path.join(
                self.workingDir, 'output', 'subject', 'histograms'))


    def __buildListMetrics(self):
        return [(self.getTensorFSLImage('dwi', 'fa'),'fsl_fa.nii.gz'),
                (self.getTensorFSLImage('dwi', 'md'),'fsl_md.nii.gz'),
                (self.getTensorFSLImage('dwi', 'ad'),'fsl_ad.nii.gz'),
                (self.getTensorFSLImage('dwi', 'rd'),'fsl_rd.nii.gz'),
                (self.getTensorDIPYImage('dwi', 'fa'),'dipy_fa.nii.gz'),
                (self.getTensorDIPYImage('dwi', 'md'),'dipy_md.nii.gz'),
                (self.getTensorDIPYImage('dwi', 'ad'),'dipy_ad.nii.gz'),
                (self.getTensorDIPYImage('dwi', 'rd'),'dipy_rd.nii.gz'),
                (self.getTensorMRTRIXImage('dwi', 'fa'),'mrtrix_fa.nii.gz'),
                (self.getTensorMRTRIXImage('dwi', 'md'),'mrtrix_md.nii.gz'),
                (self.getTensorMRTRIXImage('dwi', 'ad'),'mrtrix_ad.nii.gz'),
                (self.getTensorMRTRIXImage('dwi', 'rd'),'mrtrix_rd.nii.gz'),
                (self.getHardiMRTRIXImage('dwi', 'nufo'), 'mrtrix_nufo.nii.gz'),
                (self.getHardiDIPYImage('dwi', 'nufo'), 'dipy_nufo.nii.gz')]


    def __getConfigFile(self, prefix, defaultFile):

        target = self.getPreparationImage(prefix, None, 'json')
        if target:
            util.symlink(target, self.buildName(target, None, 'json'))
        else:
            defaultFileName = '{}.json'.format(defaultFile)
            defaultFileLink = os.path.join(
                self.toadDir,
                "templates",
                "tractometry",
                defaultFileName,
            )
            target = defaultFileLink
            util.copy(defaultFileLink, self.workingDir, defaultFileName)
        return target

    '''
    def qaSupplier(self):
        """Create and supply images for the report generated by qa task

        """
        qaImages = Images()

        return qaImages
    '''
