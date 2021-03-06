"""
Test the library on desired behavior by running it on several models.
"""
import unittest
import os
import logging
import io
from nose.plugins.attrib import attr
import numpy as np

from python_subgrid.wrapper import SubgridWrapper, logger
from python_subgrid.utils import NotDocumentedError

# We don't want to know about ctypes here
# only in the test_wrapper and the wrapper itself.

EPSILON = 0.00000001

scenarios = {
    '1dpumps': {
        'path': '1dpumptest',
        'mdu_filename': "1d2d_kunstw.mdu",
    },
    '1d-democase': {
        'path': '1d-democase',
        'mdu_filename': "1D-democase.mdu",
    },
    'DelflandiPad': {
        'path': 'delfland-model-voor-3di',
        'mdu_filename': "hhdlipad.mdu",
    },
    'betondorp': {
        'path': 'betondorp',
        'mdu_filename': "betondorp.mdu",
    },
    'Kaapstad': {
        'path': 'Kaapstad',
        'mdu_filename': "Kaapstad.mdu",
    },
    'mozambique': {
        'path': 'mozambique',
        'mdu_filename': "mozambique.mdu",
    },
    'boezemstelsel-delfland': {
        'path': 'boezemstelsel-delfland',
        'mdu_filename': "Boezem_HHD.mdu",
    },
    'heerenveen': {
        'path': 'heerenveen',
        'mdu_filename': "heerenveen.mdu",
    },
}

# Use DelflandiPad by default for now
DEFAULT_SCENARIO = 'DelflandiPad'
scenario = os.environ.get('SCENARIO', DEFAULT_SCENARIO)
# By default, we look for scenario dirs in the current working directory. This
# means you need to create symlinks to them.
# Handiest is to use the ``update_testcases.sh`` script to check out
# everything into the testcases directory. This is supported by default.
# An alternative is to set the
# SCENARIO_BASEDIR environment variable.
if 'SCENARIO_BASEDIR' in os.environ:
    scenario_basedir = os.path.abspath(os.environ['SCENARIO_BASEDIR'])
elif 'testcases' in os.listdir('.'):
    scenario_basedir = os.path.abspath('testcases')
else:
    scenario_basedir = os.path.abspath('.')

default_scenario_path = os.path.join(scenario_basedir,
                                     scenarios[scenario]['path'])
models_available = os.path.exists(default_scenario_path)
msg = "Scenario models not available {}".format(default_scenario_path)

#TODO: get this to work
#@unittest.skipIf(not models_available, msg)
class LibSubgridTest(unittest.TestCase):

    def setUp(self):
        self.default_mdu = self._mdu_path(scenario)
        pass

    def tearDown(self):
        pass

    def _mdu_path(self, scenario):
        abs_path = os.path.join(scenario_basedir,
                                scenarios[scenario]['path'])
        return os.path.join(abs_path, scenarios[scenario]['mdu_filename'])

    def test_logging(self):
        subgrid = SubgridWrapper()
        foundmessage = False

        # Create a new handler
        stream = io.BytesIO()
        handler = logging.StreamHandler(stream)
        logger.addHandler(handler)

        # if the model logs it is stored in the handler
        subgrid.start()

        # flush
        handler.flush()
        foundmessage = stream.getvalue()

        # cleanup
        logger.removeHandler(handler)

        # we should have some messages
        self.assertTrue(foundmessage)

    def test_info(self):
        with SubgridWrapper() as subgrid:
            subgrid.subgrid_info()

    @attr('debug')
    def test_load(self):
        print
        print '########### test multiple load'
        for i in range(2):
            with SubgridWrapper(mdu=self.default_mdu):
                print 'test load #%r' % i

    def test_load_1d(self):
        print
        print '########### test multiple load 1d'
        for i in range(2):
            with SubgridWrapper(mdu=self._mdu_path('boezemstelsel-delfland')):
                print 'test load #%r' % i

    #@unittest.skip
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

    #@unittest.skip
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

    #@unittest.skip
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
                subgrid.discharge(
                    85830.97071920538, 448605.8983910042,
                    manhole_name, 1, 100.0)

    #@unittest.skip
    def test_manhole_mozambique(self):
        print
        print '############ test manhole mozambique'
        mdu_filename = self._mdu_path('mozambique')
        # if not os.path.exists(mdu_filename):
        #     print 'ignored'
        #     return
        with SubgridWrapper(mdu=mdu_filename) as subgrid:
            manhole_name = 'test_manhole'
            x = 695570
            y = 7806336
            discharge_value = 5000.0
            itype = 1
            subgrid.discharge(x, y, manhole_name, itype, discharge_value)
            for i in xrange(100):
                print 'doing %d...' % i
                subgrid.update(-1)

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

    @unittest.skip
    def test_manhole_workflow(self):
        print
        print '############ test manhole workflow'
        with SubgridWrapper(mdu=self.default_mdu) as subgrid:
            manhole_name = 'test_manhole'
            x = 85830.97071920538
            y = 448605.8983910042
            discharge_value = 100.0
            itype = 1
            # add it
            import numpy as np
            for i in range(5):
                deltas = np.linspace(0, 100000, num=5)
                for i, delta in enumerate(deltas):
                    subgrid.discharge(x + delta, y + delta,
                                      "%s_%s" % (manhole_name, i),
                                      itype, discharge_value)
                subgrid.update(-1)
                # reinitialize
                subgrid.initmodel()
                subgrid.update(-1)
                # remove it
                for delta in deltas:
                    subgrid.discard_manhole(x + delta, y + delta)
                # add it again
                subgrid.update(-1)

    def test_get_var_rank(self):
        with SubgridWrapper(mdu=self.default_mdu) as subgrid:
            subgrid.initmodel()
            rank = subgrid.get_var_rank('s1')
            self.assertEqual(1, rank)

    def test_get_var_type(self):
        with SubgridWrapper(mdu=self.default_mdu) as subgrid:
            subgrid.initmodel()
            typename = subgrid.get_var_type('s1')
            self.assertEqual(typename, 'double')

    def test_get_var_shape(self):
        with SubgridWrapper(mdu=self.default_mdu) as subgrid:
            subgrid.initmodel()
            shape = subgrid.get_var_shape('s1')
            self.assertGreater(shape[0], 10)

    def test_get_nd(self):
        with SubgridWrapper(mdu=self.default_mdu) as subgrid:
            subgrid.initmodel()
            arr = subgrid.get_nd('s1')
            self.assertEqual(len(arr.shape), 1)
            logging.debug(arr)

    def test_get_nd_unknown_variable(self):
        with SubgridWrapper(mdu=self.default_mdu) as subgrid:
            subgrid.initmodel()
            self.assertRaises(NotDocumentedError, subgrid.get_nd, 'reinout')

    def test_compound_rank(self):
        with SubgridWrapper(mdu=self.default_mdu) as subgrid:
            subgrid.initmodel()
            rank = subgrid.get_var_rank('pumps')
            self.assertEqual(rank, 1)

    def test_compound_type(self):
        with SubgridWrapper(mdu=self.default_mdu) as subgrid:
            subgrid.initmodel()
            type_ = subgrid.get_var_type('pumps')
            self.assertEqual(type_, 'pump')

    def test_make_compound(self):
        with SubgridWrapper(mdu=self.default_mdu) as subgrid:
            subgrid.initmodel()
            valtype = subgrid.make_compound_ctype("pumps")
            # check if the type is a pointer to the compound array type
            # types pointer->array->pumps->id
            self.assertTrue(valtype._type_.__name__.startswith(
                'COMPOUND_Array'))
            self.assertEqual(valtype._type_._type_.__name__, 'COMPOUND')

    def test_compound_getnd(self):
        with SubgridWrapper(mdu=self._mdu_path('1dpumps')) as subgrid:
            subgrid.initmodel()
            df = subgrid.get_nd('pumps')
            self.assertEqual(len(df), 1)
            logger.info(df.to_string())

    def test_remove_pump(self):
        with SubgridWrapper(mdu=self._mdu_path('1dpumps')) as subgrid:
            subgrid.initmodel()
            df = subgrid.get_nd('pumps')
            self.assertEqual(len(df), 1)
            id = df['id'].irow(0)
            logger.info(id)
            # This deletes a structure, a pump is a structure
            subgrid.discard_structure(id)
            # Now if we get the pumps again it should be empty
            df = subgrid.get_nd('pumps')
            self.assertEqual(len(df), 0)
    def test_pump_it_up(self):
        with SubgridWrapper(mdu=self._mdu_path('1dpumps')) as subgrid:
            subgrid.initmodel()
            df = subgrid.get_nd('pumps')
            self.assertEqual(len(df), 1)
            # Increase capacity of all pumps by a factor 10
            df['capacity'] = df['capacity'] * 10
            s1before = subgrid.get_nd('s1').copy()
            subgrid.update(-1)
            s1after = subgrid.get_nd('s1').copy()
            # There should be water movement now, check S1
            self.assertGreater(np.abs(s1after - s1before).sum(), 0)


    def test_pump_it_up_manual(self):
        with SubgridWrapper(mdu=self._mdu_path('1dpumps')) as subgrid:
            subgrid.initmodel()
            df = subgrid.get_nd('pumps')
            self.assertEqual(len(df), 1)
            # Get the current capacity
            # Make sure you use item(0), otherwise you get a numpy 0d type
            capacity0 = df.capacity.item(0)
            pumpid = df.id.item(0)
            # Increase capacity of all pump1 by a factor 10
            subgrid.set_structure_field("pumps", pumpid, "capacity", capacity0 * 10)
            df = subgrid.get_nd('pumps')
            self.assertEqual(df.id.item(0), pumpid)
            capacity1 = df.capacity.item(0)
            self.assertEqual(capacity1, capacity0 * 10)


    # def test_get_water_level(self):
    #     print
    #     print '########### test get water level'
    #     abs_path = os.path.join(scenario_basedir,
    #                             scenarios[scenario]['path'])
    #     load_model(abs_path, scenarios[scenario]['mdu_filename'])
    #     subgrid.initmodel()
    #     self.model_initialized = True

    #     for i in xrange(10):
    #         print 'doing %d...' % i
    #         #print libsubgrid.funcall('update',
    #                 'ctypes.byref(ctypes.c_double(-1))')
    #                 # -1 = use default model timestep.
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
    #     #     'ctypes.byref(args[1]), ctypes.byref(args[2]),
    #                                   ctypes.byref(args[3])',
    #     #     xtest, ytest, level)
    #     print "na getwaterlevel, result at (%r, %r): %r" % (
    #                      xtest, ytest, level)
    #     print 'true? %r' % (abs(level.value - -1.6409107876960418) < EPSILON)
    #     # The value is -999 now..
    #     #unittest.assertTrue((level.value - -1.6409107876960418) < EPSILON)

    #     for i in xrange(10):
    #         print 'doing %d...' % i
    #         print subgrid.update(-1) # -1 = use default model time
    #         # print libsubgrid.funcall(
    #         #     'update', 'ctypes.byref(ctypes.c_double(-1))')
    #                 # -1 = use default model timestep.

    #     result = subgrid.getwaterlevel(
    #         ctypes.byref(xtest),
    #         ctypes.byref(ytest),
    #         ctypes.byref(level)
    #     )

    #     # result = libsubgrid.funcall(
    #     #     'GETWATERLEVEL',
    #     #     'ctypes.byref(args[1]), ctypes.byref(args[2]),
    #           ctypes.byref(args[3])',
    #     #     xtest, ytest, level)
    #     print "na getwaterlevel2, result at (%r, %r): %r" % (
    #                xtest, ytest, level)
    #     # After one run it has this value... don't know if we have to check,
    #     # but it's a got change follower
    #     # The value is -999 now..
    #     print 'true? %r' % (abs(level.value - -1.4157227881505232) < EPSILON)
    #     print 'true? %r' % (abs(level.value - -1.2157227881505232) < EPSILON)
    #     #unittest.assertTrue((level.value - -1.4157227881505232) < EPSILON)

    #     #libsubgrid.funcall('finalizemodel')

    def test_changebathy(self):
        print
        print '########### test change bathy'
        with SubgridWrapper(mdu=self.default_mdu) as subgrid:
            for i in xrange(5):
                print 'doing %d...' % i
                print subgrid.update(-1)  # -1 = use default model time

            xc = 250808.205511
            yc = 589490.224168
            sz = 15
            bval = -11.23
            bmode = 0  # 0 = relative, 1 = absolute

            subgrid.changebathy(xc, yc, sz, bval, bmode)

            bval = 5
            bmode = 1  # 0 = relative, 1 = absolute

            subgrid.changebathy(xc, yc, sz, bval, bmode)

            for i in xrange(5):
                print 'doing %d...' % i
                print subgrid.update(-1)  # -1 = use default model time

    def test_changebathy_heerenveen(self):
        print
        print '########### test change bathy heerenveen'
        with SubgridWrapper(mdu=self._mdu_path('heerenveen')) as subgrid:
            for i in xrange(5):
                print 'doing %d...' % i
                print subgrid.update(-1)  # -1 = use default model time

            xc = 188733.
            yc = 553957.
            sz = 70
            bval = -0.5
            bmode = 1  # 0 = relative, 1 = absolute

            print 'changing bathymetry...'
            subgrid.changebathy(xc, yc, sz, bval, bmode)

            print 'continue simulation...'
            for i in xrange(5):
                print 'doing %d...' % i
                print subgrid.update(-1)  # -1 = use default model time

    def test_link_table(self):
        with SubgridWrapper(mdu=self._mdu_path('1d-democase')) as subgrid:
            # Note the copy, variables get reused, so copy them if you're calling
            # get_nd, multiple times
            data = dict(branch=subgrid.get_nd('link_branchid').copy(),
                        chainage=subgrid.get_nd('link_chainage').copy(),
                        idx=subgrid.get_nd('link_idx').copy())
            df = pandas.DataFrame(data)
            self.assertEqual(df.idx.item(0), 249)
            self.assertEqual(df.idx.item(-1), 248)
    # # def test_changebathy2(self):
    # #     """Known crashing case"""
    # #     print
    # #     print '########### test change bathy2'
    # #     abs_path = os.path.join(scenario_basedir,
    #                 scenarios['betondorp']['path'])
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
    # #         'ctypes.c_double(args[1]), ctypes.c_double(args[2]),
    #             ctypes.c_double(args[3]), ctypes.c_double(args[4]),
    #             ctypes.c_int(args[5])',
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
