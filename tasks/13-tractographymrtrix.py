# -*- coding: utf-8 -*-
import numpy
import os
from core.toad.generictask import GenericTask
from lib import mriutil
from lib.images import Images


__author__ = "Mathieu Desrosiers"
__copyright__ = "Copyright (C) 2014, TOAD"
__credits__ = ["Mathieu Desrosiers"]


class TractographyMrtrix(GenericTask):


    def __init__(self, subject):
        GenericTask.__init__(self, subject, 'upsampling', 'hardimrtrix', 'masking', 'registration','qa')
        self.__tckDetRoiTrk = None
        self.__tckProbRoiTrk = None
        self.__tckgenRoiTrk = None
        self.__tcksiftRoiTrk = None

    def implement(self):

        tt5 = self.getRegistrationImage("tt5", "register")
        seed_gmwmi = self.getMaskingImage("tt5", ["register", "5tt2gmwmi"])
        #@TODO reactivate brodmann = self.getRegistrationImage("brodmann", "resample")
        aal2 =  self.getRegistrationImage("aal2", "resample")
        networks7 =  self.getRegistrationImage("networks7", "resample")
        norm = self.getRegistrationImage("norm", "resample")

        mask253 = self.getMaskingImage('aparc_aseg', ['253', 'mask'])
        mask1024= self.getMaskingImage('aparc_aseg', ['1024', 'mask'])

        dwi = self.getUpsamplingImage('dwi', 'upsample')

        bFile = self.getUpsamplingImage('grad', None, 'b')
        mask = self.getRegistrationImage('mask', 'resample')

        #tensor part
        if 'deterministic' in self.get('algorithm'):
            tckDet = self.__tckgenTensor(dwi, self.buildName(dwi, 'tensor_det', 'tck'), mask, tt5, seed_gmwmi, bFile, 'Tensor_Det')
            self.__plotConnectome(tckDet, aal2, "aal2_lut", "aal2")
            self.__plotConnectome(tckDet, networks7, "networks7_lut", "networks7")
            tckDetRoi = self.__tckedit(tckDet, mask253, self.buildName(tckDet, 'roi','tck'))
            tckDetRoiTrk = mriutil.tck2trk(tckDetRoi, norm, self.buildName(tckDetRoi, None, 'trk'))
            self.__tckDetRoiTrk = tckDetRoiTrk


        if 'probabilistic' in self.get('algorithm'):
            tckProb = self.__tckgenTensor(dwi, self.buildName(dwi, 'tensor_prob', 'tck'), mask, tt5, seed_gmwmi, bFile, 'Tensor_Prob')
            self.__plotConnectome(tckProb, aal2, "aal2_lut", "aal2")
            self.__plotConnectome(tckProb, networks7, "networks7_lut", "networks7")
            tckProbRoi = self.__tckedit(tckProb, mask253, self.buildName(tckProb, 'roi','tck'))
            tckProbRoiTrk = mriutil.tck2trk(tckProbRoi, norm , self.buildName(tckProbRoi, None, 'trk'))
            self.__tckProbRoiTrk = tckProbRoiTrk


        if 'hardi' in self.get('algorithm'):
            csd =  self.getHardimrtrixImage('dwi','csd')
            hardiTck = self.__tckgenHardi(csd, self.buildName(csd, 'hardi_prob', 'tck'), tt5)
            self.__plotConnectome(hardiTck, aal2, "aal2_lut", "aal2")
            self.__plotConnectome(hardiTck, networks7, "networks7_lut", "networks7")
            hardiTckRoi = self.__tckedit(hardiTck, mask253, self.buildName(hardiTck, 'roi','tck'))
            tckgenRoiTrk = mriutil.tck2trk(hardiTckRoi, norm , self.buildName(hardiTckRoi, None, 'trk'))
            self.__tckgenRoiTrk = tckgenRoiTrk

            if 'sift' in self.get('algorithm'):
                tcksift = self.__tcksift(hardiTck, csd)
                self.__plotConnectome(tcksift, aal2, "aal2_lut", "aal2")
                self.__plotConnectome(tcksift, networks7, "networks7_lut", "networks7")
                tcksiftRoi = self.__tckedit(tcksift, mask253, self.buildName(tcksift, 'roi', 'tck'))
                tcksiftRoiTrk = mriutil.tck2trk(tcksiftRoi, norm , self.buildName(tcksiftRoi, None, 'trk'))
                self.__tcksiftRoiTrk = tcksiftRoiTrk



    def __tckedit(self, source, roi, target, downsample= "2"):
        """ perform various editing operations on track files.

        Args:
            source: the input track file(s)
            roi:    specify an inclusion region of interest, as either a binary mask image, or as a sphere
                    using 4 comma-separared values (x,y,z,radius)
            target: the output track file
            downsample: increase the density of points along the length of the streamline by some factor

        Returns:
            the output track file
        """
        self.info("Starting tckedit creation from mrtrix on {}".format(source))
        tmp = self.buildName(source, "tmp", "tck")
        mriutil.tckedit(source, roi, tmp, downsample)
        return self.rename(tmp, target)


    def __tckgenTensor(self, source, target, mask = None, act = None , seed_gmwmi = None, bFile = None, algorithm = "iFOD2"):
        """ perform streamlines tractography.

             the image containing the source data. The type of data
             depends on the algorithm used:
             - FACT: the directions file (each triplet of volumes is
             the X,Y,Z direction of a fibre population).
             - iFOD1/2 & SD_Stream: the SH image resulting from CSD.
             - Nulldist & SeedTest: any image (will not be used).
             - TensorDet / TensorProb: the DWI image.

        Args:
            source: the image containing the source data.
            target: the output file containing the tracks generated.
            bFile: specify the diffusion-weighted gradient scheme used in the acquisition.
            mask: specify a masking region of interest, as a binary mask image.
            act: use the Anatomically-Constrained Tractography framework during tracking
            seed_gmwmi: seed from the grey matter - white matter interface (only valid if using ACT framework)
            algorithm: the tractography algorithm to use. default: iFOD2

        Returns:
            The resulting streamlines tractography filename generated

        """
        self.info("Starting tckgen creation from mrtrix on {}".format(source))
        tmp = self.buildName(source, "tmp", "tck")
        cmd = "tckgen {} {}  -mask {} -act {} -seed_gmwmi {} -number {} -algorithm {} -downsample {} -nthreads {} -quiet"\
            .format(source, tmp, mask,  act, seed_gmwmi, self.get('number_tracks'), algorithm, self.get('downsample'), self.getNTreadsMrtrix())

        if bFile is not None:
            cmd += " -grad {}".format(bFile)

        self.launchCommand(cmd)
        return self.rename(tmp, target)


    def __tckgenHardi(self, source, target, act = None, bFile = None, algorithm = "iFOD2"):
        """
         perform streamlines tractography.

             the image containing the source data. The type of data
             depends on the algorithm used:
             - FACT: the directions file (each triplet of volumes is
             the X,Y,Z direction of a fibre population).
             - iFOD1/2 & SD_Stream: the SH image resulting from CSD.
             - Nulldist & SeedTest: any image (will not be used).
             - TensorDet / TensorProb: the DWI image.

        Args:
            source: the image containing the source data.
            target: the output file name
            bFile: specify the diffusion-weighted gradient scheme used in the acquisition.
            mask: specify a masking region of interest, as a binary mask image.
            act: use the Anatomically-Constrained Tractography framework during tracking
            algorithm: the tractography algorithm to use. default: iFOD2

        Returns:
            The resulting streamlines tractography filename generated
        """

        self.info("Starting tckgen creation from mrtrix on {}".format(source))
        tmp = self.buildName(source, "tmp", "tck")
        cmd = "tckgen {} {} -act {} -seed_dynamic {} -step {} -maxlength {} -number {} -algorithm {} -backtrack -downsample {} -nthreads {} -quiet"\
            .format(source, tmp, act, source, self.get('step'), self.get('maxlength'), self.get( 'number_tracks'), algorithm, self.get('downsample'), self.getNTreadsMrtrix())

        if bFile is not None:
            cmd += " -grad {}".format(bFile)

        self.launchCommand(cmd)
        return self.rename(tmp, target)


    def __tcksift(self, source, csd):
        """ filter a whole-brain fibre-tracking data set such that the streamline densities match the FOD lobe integral.

        Args:
            source: the input track file.
            csd: input image containing the spherical harmonics of the fibre orientation distributions

        Returns:
            The resulting output filtered tracks file

        """
        tmp = self.buildName(source, "tmp", "tck")
        target = self.buildName(source, 'tcksift','.tck')
        self.info("Starting tcksift creation from mrtrix on {}".format(source))

        cmd = "tcksift {} {} {} -nthreads {} -quiet".format(source, csd, tmp, self.getNTreadsMrtrix())
        self.launchCommand(cmd)

        return self.rename(tmp, target)


    def __plotConnectome(self, source, atlas, lut, prefix):
        """ perform connectomme steps.

        Args:
            source: the input track file
            atlas: the atlas
            lut: an compatible itksnap lut file

        Returns:
            a connectome png image
        """
        if lut is not None:
            lutFile= os.path.join(self.toadDir, "templates", "lookup_tables", self.get("template", lut))
        else:
            lutFile= None

        if self.get('arguments', 'debug'):
            self.info('Source file: {}'.format(source))
            self.info('Atlas file: {}'.format(atlas))
            self.info('Lut file location: {}'.format(lutFile))
             
        connectome = self.__tck2connectome(source, atlas, self.buildName(source, [ prefix , 'connectome'], 'csv'))
        connectomeNormalize = self.__normalizeConnectome(connectome, self.buildName(connectome, 'normalize', 'csv'))
        pngImage = mriutil.plotConnectome(connectomeNormalize, self.buildName(connectomeNormalize, None, "png"), lutFile)
        return pngImage


    def __tck2connectome(self, source, nodes, target):
        """ generate a connectome matrix from a streamlines file and a node parcellation image

        Args:
            source: the input track file
            nodes: the input parcellation image
            target: the output .csv file containing edge weights

        Returns:
            The resulting .cvs file name

        """
        self.info("Starting tck2connectome from mrtrix on {}".format(source))
        tmp = self.buildName(source, "tmp", "csv")
        cmd = "tck2connectome {} {} {} -quiet -zero_diagonal -nthreads {}".format(source, nodes, tmp, self.getNTreadsMrtrix() )

        self.launchCommand(cmd)
        return self.rename(tmp, target)


    def __normalizeConnectome(self, source, target):
        """ generate a connectome matrix which each row is normalize

            if you sum each element of a given lines the result will equal 1.00

        Args:
            source: a input .csv file containing edge weights. see __tck2connectome
            target: the output .csv file containing normalize results

        Returns:
            The resulting .cvs file name

        """
        matrix = numpy.genfromtxt(source, delimiter=' ')
        matrix = numpy.add(matrix, numpy.matrix.transpose(matrix))

        with numpy.errstate(invalid='ignore'):
            for index, row in enumerate(matrix):
                    matrix[index] = numpy.divide(row, row.sum())

        matrix[numpy.isnan(matrix)] = 0.0
        numpy.savetxt(target, matrix, delimiter=' ', fmt='%0.4f')
        return target


    def isIgnore(self):
        if self.get("ignore"):
            return True

        elif self.get('hardimrtrix', 'ignore'):
            self.warning('This task depend on hardi mrtrix task that is set to ignore.')
            return True

        return False


    def meetRequirement(self):
        #@TODO add brain mask and 5tt as requierement
        return Images((self.getUpsamplingImage('dwi','upsample'), 'upsampled diffusion weighted'),
                  (self.getUpsamplingImage('grad', None, 'b'), '.b gradient encoding file'),
                  (self.getRegistrationImage("mask", "resample"), 'mask resampled'),
                  (self.getRegistrationImage("brodmann", "resample"), 'resampled brodmann area'),
                  (self.getRegistrationImage("aal2", "resample"), 'resampled aal2 area'),
                  (self.getRegistrationImage("networks7", "resample"), 'resampled seven networks area'),
                  (self.getRegistrationImage("norm", "resample"), 'brain resampled'),
                  (self.getMaskingImage('aparc_aseg',['253','mask']), 'area 253 from aparc_aseg'),
                  (self.getRegistrationImage("tt5", "register"),'5tt register'),
                  (self.getMaskingImage('aparc_aseg',['1024','mask']), 'area 1024 from aparc_aseg'),
                  (self.getMaskingImage("tt5", ["register", "5tt2gmwmi"]), 'grey matter, white matter interface'))



    def isDirty(self):

        images = Images()
        if 'deterministic' in self.get('algorithm'):
            images.extend(Images((self.getImage('dwi', 'tensor_det', 'tck'), "deterministic tensor connectome matrix from a streamlines"),
                  (self.getImage('dwi', ['tensor_det','aal2', 'connectome', 'normalize'], 'csv'), "Aal2 normalize deterministic tensor connectome matrix from a streamlines csv"),
                  (self.getImage('dwi', ['tensor_det', 'networks7' ,'connectome', 'normalize'], 'csv'), "Seven networks normalize deterministic tensor connectome matrix from a streamlines csv")))

        if 'probabilistic' in self.get('algorithm'):
            images.extend(Images((self.getImage('dwi', 'tensor_prob', 'tck'), "probabilistic tensor connectome matrix from a streamlines"),
                  (self.getImage('dwi', ['tensor_prob', 'aal2', 'connectome', 'normalize'], 'csv'), "Aal2 normalize probabilistic tensor connectome matrix from a streamlines csv"),
                  (self.getImage('dwi', ['tensor_prob', 'networks7' ,'connectome', 'normalize'], 'csv'), "Seven networks normalize probabilistic tensor connectome matrix from a streamlines csv")))

        if 'hardi' in self.get('algorithm'):
            images.append((self.getImage('dwi', 'hardi_prob', 'tck'), "tckgen hardi probabilistic streamlines tractography"))


        if 'sift' in self.get('algorithm'):
            images.extend(Images((self.getImage('dwi', 'tcksift', 'tck'), 'tcksift'),
                  (self.getImage('dwi', ['tcksift', 'aal2', 'connectome', 'normalize'], 'csv'), 'Aal2 normalize connectome matrix from a tcksift csv'),
                  (self.getImage('dwi', ['tcksift', 'networks7', 'connectome', 'normalize'], 'csv'), 'Seven networks normalize connectome matrix from a tcksift csv')))

        return images

    def qaSupplier(self):
        """Create and supply images for the report generated by qa task

        """
        qaImages = Images()

        information = 'Warning: due to storage restriction streamlines were downsampled. Even if there is no difference in structural connectivity you should be careful if you want to compute metrics along streamlines.'
        qaImages.setInformation(information)

        #get images
        norm = self.getRegistrationImage("norm", "resample")
        mask253 = self.getMaskingImage('aparc_aseg',['253','mask'])

        #images production
        if self.__tckDetRoiTrk is not None:
            tensorDetPng = self.createVtkPng(self.__tckDetRoiTrk, norm, mask253)#self.getImage('dwi', ['tensor_det', 'roi'], 'png')
            tensorAal2DetPlot = self.getImage('dwi', ['tensor_det', 'aal2', 'connectome', 'normalize'], 'png')
            tensorNetworks7DetPlot = self.getImage('dwi', ['tensor_det', 'networks7', 'connectome', 'normalize'], 'png')

            qaImages.extend(Images((tensorDetPng, 'fiber crossing aparc_aseg area 253 from a deterministic tensor streamlines'),
                    (tensorAal2DetPlot,'Aal2 normalize connectome matrix from a deterministic tensor streamlines'),
                    (tensorNetworks7DetPlot,'Seven networks normalize connectome matrix from a deterministic tensor streamlines')))

        if self.__tckProbRoiTrk is not None:
            tensorProbPng = self.createVtkPng(self.__tckProbRoiTrk, norm, mask253)#self.getImage('dwi', ['tensor_prob', 'roi'], 'png')
            tensorAal2ProbPlot = self.getImage('dwi', ['tensor_prob', 'aal2', 'connectome', 'normalize'], 'png')
            tensorNetworks7ProbPlot = self.getImage('dwi', ['tensor_prob', 'networks7', 'connectome', 'normalize'], 'png')

            qaImages.extend(Images((tensorProbPng, 'fiber crossing aparc_aseg area 253 from a probabilistic tensor streamlines'),
                    (tensorAal2ProbPlot,'Aal2 normalize connectome matrix from a probabilistic tensor streamlines'),
                    (tensorNetworks7ProbPlot,'Seven networks normalize connectome matrix from a probabilistic tensor streamlines')))

        if self.__tckgenRoiTrk is not None:
            hardiProbPng = self.createVtkPng(self.__tckgenRoiTrk, norm, mask253)#self.getImage('dwi', ['hardi_prob', 'roi'], 'png')
            hardiAal2ProbPlot = self.getImage('dwi', ['hardi_prob', 'aal2', 'connectome', 'normalize'], 'png')
            hardiNetworks7ProbPlot = self.getImage('dwi', ['hardi_prob', 'networks7', 'connectome', 'normalize'], 'png')

            qaImages.extend(Images((hardiProbPng, 'fiber crossing aparc_aseg area 253 from a probabilistic hardi streamlines'),
                    (hardiAal2ProbPlot, 'Aal2 normalize connectome matrix from a probabilistic hardi streamlines'),
                    (hardiNetworks7ProbPlot, 'Seven networks normalize connectome matrix from a probabilistic hardi streamlines')))

        if self.__tcksiftRoiTrk is not None:

            tcksiftPng = self.createVtkPng(self.__tcksiftRoiTrk, norm, mask253)#self.getImage('dwi', ['tcksift', 'roi'], 'png')
            tcksiftAal2Plot = self.getImage('dwi', ['tcksift', 'aal2', 'connectome', 'normalize'], 'png')
            tcksiftNetworks7Plot = self.getImage('dwi', ['tcksift', 'networks7', 'connectome', 'normalize'], 'png')

            qaImages.extend(Images((tcksiftPng, 'fiber crossing aparc_aseg area 253 from a probabilistic tensor streamlines'),
                    (tcksiftAal2Plot, 'Aal2 tcksift'),
                    (tcksiftNetworks7Plot, 'Seven networks tcksift')))

        return qaImages
