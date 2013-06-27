"""
Test the library on desired behavior by running it on several models.
"""
import unittest
import os
import logging

# We don't want to know about ctypes here, only in the test_wrapper and the wrapper itself.

from python_subgrid.wrapper import SubgridWrapper


EPSILON = 0.00000001

scenarios = {
    'DelflandiPad': {
        'name': 'Delfland',
        'path': 'DelflandiPad',
        'mdu_filename': "DelflandiPad.mdu",
        'asc_filename': 'ahn_guts_v4.asc'  # TODO: read from mdu
    },
    'hunzeenaas': {
        'name': 'Hunze en Aas',
        'path': 'hunzeenaas',
        'mdu_filename': "hunzeenaas.mdu",
        'asc_filename': 'h25m.asc'  # TODO: read from mdu
    },
    'betondorp': {
        'name': 'Betondorp',
        'path': 'betondorp',
        'mdu_filename': "betondorp.mdu",
        'asc_filename': 'betondorp_selectie2.asc'  # TODO: read from mdu
    },
}
DEFAULT_SCENARIO = 'DelflandiPad'
if 'SCENARIO' in os.environ:
    DEFAULT_SCENARIO = os.environ['SCENARIO']

# By default, we look for scenario dirs in the current working directory. This
# means you need to create symlinks to them. An alternative is to set the
# SCENARIO_BASEDIR environment variable.
scenario_basedir = os.getcwd()
logging.debug("environment: {}".format(os.environ))
if 'SCENARIO_BASEDIR' in os.environ:
    scenario_basedir = os.path.abspath(os.environ['SCENARIO_BASEDIR'])

MODELS_AVAILABLE = os.path.exists(os.path.join(scenario_basedir,
                                               DEFAULT_SCENARIO))


@unittest.skipIf(not MODELS_AVAILABLE, "Scenario models not available")
class LibSubgridTest(unittest.TestCase):

    def setUp(self):
        self.default_mdu = self._mdu_path(DEFAULT_SCENARIO)
        pass

    def tearDown(self):
        pass

    def _mdu_path(self, scenario):
        abs_path = os.path.join(scenario_basedir,
                                scenarios[scenario]['path'])
        return os.path.join(abs_path, scenarios[scenario]['mdu_filename'])

    def test_info(self):
        with SubgridWrapper() as subgrid:
            subgrid.subgrid_info()

    def test_load(self):
        print
        print '########### test multiple load'
        for i in range(2):
            with SubgridWrapper(mdu=self.default_mdu):
                print 'test load #%r' % i

    # def test_arraypointer(self):
    #     """"arrays: see bmi.py:get_nd, get , set / rank, shape, type"""
    #     print
    #     print '########### test array pointer'
    #     import numpy as np
    #     a = ndpointer(
    #         dtype='double', ndim=3, shape=(2,3,4), flags='F')

    #     subgrid.subgrid_arraypointer(ctypes.byref(a))
    #     print np.reshape(np.asarray(a).ravel(), [2,3,4], order='F')
    #     """
    #     [[[ 1.  1.  1.  1.]
    #     [ 1.  1.  1.  1.]
    #     [ 1.  1.  1.  1.]]

    #     [[ 2.  2.  2.  2.]
    #     [ 2.  2.  2.  2.]
    #     [ 2.  2.  2.  2.]]]
    #     """

    def test_timesteps(self):
        print
        print '########### test timesteps'
        with SubgridWrapper(mdu=self.default_mdu) as subgrid:
            for i in xrange(10):
                print 'doing %d...' % i
                # print libsubgrid.funcall(
                #     'update',
                #     'ctypes.byref(ctypes.c_double(-1))')
                print subgrid.update(-1)
                # -1 = use default model timestep.

    def test_dropinstantrain(self):
        with SubgridWrapper(mdu=self.default_mdu) as subgrid:
            subgrid.initmodel()
            self.model_initialized = True

            x = 85830.97071920538
            y = 448605.8983910042
            clouddiam = 100.0
            rainfall = 100.0
            # do ome timesteps
            for i in xrange(10):
                # rain
                subgrid.dropinstantrain(x, y, clouddiam, rainfall)
                # compute
                subgrid.update(-1)

    def test_manhole(self):
        print
        print '############ test manhole'
        with SubgridWrapper(mdu=self.default_mdu) as subgrid:
            manhole_name = 'test_manhole'
            x = 85830.97071920538
            y = 448605.8983910042
            discharge_value = 100.0
            itype = 1
            subgrid.discharge(x, y, manhole_name, itype, discharge_value)
            for i in xrange(10):
                print 'doing %d...' % i
                subgrid.update(-1)
                subgrid.discharge(85830.97071920538, 448605.8983910042, manhole_name, 1, 100.0)

    def test_discard_manhole(self):
        print
        print '############ test discard manhole'
        with SubgridWrapper(mdu=self.default_mdu) as subgrid:
            manhole_name = 'test_manhole'
            x = 85830.97071920538
            y = 448605.8983910042
            discharge_value = 100.0
            itype = 1
            subgrid.discharge(x, y, manhole_name, itype, discharge_value)
            subgrid.discard_manhole(x, y)

    def test_rain(self):
        print
        print '############ test rain'
        with SubgridWrapper(mdu=self.default_mdu) as subgrid:
            subgrid.initmodel()
            x = 85830.97071920538
            y = 448605.8983910042
            clouddiam = 100.0
            rainfall = 0.01
            print 'going to do some timesteps'
            for i in xrange(10):
                print 'doing %d...' % i
                subgrid.dropinstantrain(x, y, clouddiam, rainfall)
                subgrid.update(-1)

    # def test_get_water_level(self):
    #     print
    #     print '########### test get water level'
    #     abs_path = os.path.join(scenario_basedir,
    #                             scenarios[DEFAULT_SCENARIO]['path'])
    #     load_model(abs_path, scenarios[DEFAULT_SCENARIO]['mdu_filename'])
    #     subgrid.initmodel()
    #     self.model_initialized = True

    #     for i in xrange(10):
    #         print 'doing %d...' % i
    #         #print libsubgrid.funcall('update',
    #                 'ctypes.byref(ctypes.c_double(-1))') # -1 = use default model timestep.
    #         print subgrid.update(-1) # -1 = use default model time
    #     level = ctypes.c_double(-1234.0)
    #     #level_p = ctypes.POINTER(0.0) #ctypes.c_double(0.0)
    #     xtest = ctypes.c_double(251929.987738)
    #     ytest = ctypes.c_double(589375.641241)

    #     result = subgrid.getwaterlevel(
    #         ctypes.byref(xtest),
    #         ctypes.byref(ytest),
    #         ctypes.byref(level)
    #     )
    #     # result = libsubgrid.funcall(
    #     #     'GETWATERLEVEL',
    #     #     'ctypes.byref(args[1]), ctypes.byref(args[2]), ctypes.byref(args[3])',
    #     #     xtest, ytest, level)
    #     print "na getwaterlevel, result at (%r, %r): %r" % (xtest, ytest, level)
    #     print 'true? %r' % (abs(level.value - -1.6409107876960418) < EPSILON)
    #     # The value is -999 now..
    #     #unittest.assertTrue((level.value - -1.6409107876960418) < EPSILON)

    #     for i in xrange(10):
    #         print 'doing %d...' % i
    #         print subgrid.update(-1) # -1 = use default model time
    #         # print libsubgrid.funcall(
    #         #     'update', 'ctypes.byref(ctypes.c_double(-1))') # -1 = use default model timestep.

    #     result = subgrid.getwaterlevel(
    #         ctypes.byref(xtest),
    #         ctypes.byref(ytest),
    #         ctypes.byref(level)
    #     )

    #     # result = libsubgrid.funcall(
    #     #     'GETWATERLEVEL',
    #     #     'ctypes.byref(args[1]), ctypes.byref(args[2]), ctypes.byref(args[3])',
    #     #     xtest, ytest, level)
    #     print "na getwaterlevel2, result at (%r, %r): %r" % (xtest, ytest, level)
    #     # After one run it has this value... don't know if we have to check,
    #     # but it's a got change follower
    #     # The value is -999 now..
    #     print 'true? %r' % (abs(level.value - -1.4157227881505232) < EPSILON)
    #     print 'true? %r' % (abs(level.value - -1.2157227881505232) < EPSILON)
    #     #unittest.assertTrue((level.value - -1.4157227881505232) < EPSILON)

    #     #libsubgrid.funcall('finalizemodel')

    # def test_changebathy(self):
    #     print
    #     print '########### test change bathy'
    #     abs_path = os.path.join(scenario_basedir, scenarios[DEFAULT_SCENARIO]['path'])
    #     load_model(abs_path, scenarios[DEFAULT_SCENARIO]['mdu_filename'])
    #     subgrid.initmodel()
    #     self.model_initialized = True

    #     for i in xrange(10):
    #         print 'doing %d...' % i
    #         print subgrid.update(-1) # -1 = use default model time

    #     xc = 250808.205511
    #     yc = 589490.224168
    #     sz = 15
    #     bval = -11.23
    #     bmode = 0

    #     subgrid.changebathy(xc, yc, sz, bval, bmode)

    #     # libsubgrid.funcall(
    #     #     'changebathy',
    #     #     'ctypes.c_double(args[1]), ctypes.c_double(args[2]), ctypes.c_double(args[3]), ctypes.c_double(args[4]), ctypes.c_int(args[5])',
    #     #     xc, yc, sz, bval, bmode)

    #     #libsubgrid.funcall('finalizemodel')

    # # def test_changebathy2(self):
    # #     """Known crashing case"""
    # #     print
    # #     print '########### test change bathy2'
    # #     abs_path = os.path.join(scenario_basedir, scenarios['betondorp']['path'])
    # #     load_model(abs_path, scenarios['betondorp']['mdu_filename'])
    # #     libsubgrid.funcall('initmodel')
    # #     self.model_initialized = True

    # #     xc = 125209.332
    # #     yc = 483799.384
    # #     sz = 50.000
    # #     bval = -3.000
    # #     bmode = 0

    # #     libsubgrid.funcall(
    # #         'changebathy',
    # #         'ctypes.c_double(args[1]), ctypes.c_double(args[2]), ctypes.c_double(args[3]), ctypes.c_double(args[4]), ctypes.c_int(args[5])',
    # #         xc, yc, sz, bval, bmode)
    # #     #libsubgrid.funcall('finalizemodel')

    def test_floodfill(self):
        print
        print '########### test floodfill'
        with SubgridWrapper(mdu=self._mdu_path('betondorp')) as subgrid:

            x = 125176.875732
            y = 483812.708018
            level = -1.00
            mode = 1

            subgrid.floodfilling(x, y, level, mode)

            x = 125176.875732
            y = 483812.708018
            level = -0.80
            mode = 1

            subgrid.floodfilling(x, y, level, mode)

            x = 125176.875732
            y = 483812.708018
            level = -0.60
            mode = 1

            subgrid.floodfilling(x, y, level, mode)

            x = 125176.875732
            y = 483812.708018
            level = -0.40
            mode = 1

            subgrid.floodfilling(x, y, level, mode)

            x = 125176.875732
            y = 483812.708018
            level = 0.20
            mode = 1

            subgrid.floodfilling(x, y, level, mode)


# For Martijn
if __name__ == '__main__':
    unittest.main()
