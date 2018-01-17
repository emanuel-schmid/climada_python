"""
Test imp_funcsFuncsExcel class.
"""

import unittest

from climada.entity.impact_funcs.source_excel import ImpactFuncsExcel
from climada.util.constants import ENT_DEMO_XLS, ENT_TEMPLATE_XLS

class TestReader(unittest.TestCase):
    """Test reader functionality of the imp_funcsFuncsExcel class"""

    def test_demo_file_pass(self):
        """ Read demo excel file"""
        # Read demo excel file
        imp_funcs = ImpactFuncsExcel()
        description = 'One single file.'
        imp_funcs.read(ENT_DEMO_XLS, description)

        # Check results
        n_funcs = 2
        hazard = 'TC'
        first_id = 1
        second_id = 3

        self.assertEqual(len(imp_funcs.data), 1)
        self.assertEqual(len(imp_funcs.data[hazard]), n_funcs)

        # first function
        self.assertEqual(imp_funcs.data[hazard][first_id].id, 1)
        self.assertEqual(imp_funcs.data[hazard][first_id].name,
                         'Tropical cyclone default')
        self.assertEqual(imp_funcs.data[hazard][first_id].intensity_unit, \
                         'm/s')

        self.assertEqual(imp_funcs.data[hazard][first_id].intensity.shape, \
                         (9,))
        self.assertEqual(imp_funcs.data[hazard][first_id].intensity[0], 0)
        self.assertEqual(imp_funcs.data[hazard][first_id].intensity[1], 20)
        self.assertEqual(imp_funcs.data[hazard][first_id].intensity[2], 30)
        self.assertEqual(imp_funcs.data[hazard][first_id].intensity[3], 40)
        self.assertEqual(imp_funcs.data[hazard][first_id].intensity[4], 50)
        self.assertEqual(imp_funcs.data[hazard][first_id].intensity[5], 60)
        self.assertEqual(imp_funcs.data[hazard][first_id].intensity[6], 70)
        self.assertEqual(imp_funcs.data[hazard][first_id].intensity[7], 80)
        self.assertEqual(imp_funcs.data[hazard][first_id].intensity[8], 100)

        self.assertEqual(imp_funcs.data[hazard][first_id].mdd.shape, (9,))
        self.assertEqual(imp_funcs.data[hazard][first_id].mdd[0], 0)
        self.assertEqual(imp_funcs.data[hazard][first_id].mdd[8], 0.41079600)

        self.assertEqual(imp_funcs.data[hazard][first_id].paa.shape, (9,))
        self.assertEqual(imp_funcs.data[hazard][first_id].paa[0], 0)
        self.assertEqual(imp_funcs.data[hazard][first_id].paa[8], 1)

        # second function
        self.assertEqual(imp_funcs.data[hazard][second_id].id, 3)
        self.assertEqual(imp_funcs.data[hazard][second_id].name,
                         'TC Building code')
        self.assertEqual(imp_funcs.data[hazard][first_id].intensity_unit, \
                         'm/s')

        self.assertEqual(imp_funcs.data[hazard][second_id].intensity.shape, \
                         (9,))
        self.assertEqual(imp_funcs.data[hazard][second_id].intensity[0], 0)
        self.assertEqual(imp_funcs.data[hazard][second_id].intensity[1], 20)
        self.assertEqual(imp_funcs.data[hazard][second_id].intensity[2], 30)
        self.assertEqual(imp_funcs.data[hazard][second_id].intensity[3], 40)
        self.assertEqual(imp_funcs.data[hazard][second_id].intensity[4], 50)
        self.assertEqual(imp_funcs.data[hazard][second_id].intensity[5], 60)
        self.assertEqual(imp_funcs.data[hazard][second_id].intensity[6], 70)
        self.assertEqual(imp_funcs.data[hazard][second_id].intensity[7], 80)
        self.assertEqual(imp_funcs.data[hazard][second_id].intensity[8], 100)

        self.assertEqual(imp_funcs.data[hazard][second_id].mdd.shape, (9,))
        self.assertEqual(imp_funcs.data[hazard][second_id].mdd[0], 0)
        self.assertEqual(imp_funcs.data[hazard][second_id].mdd[8], 0.4)

        self.assertEqual(imp_funcs.data[hazard][second_id].paa.shape, (9,))
        self.assertEqual(imp_funcs.data[hazard][second_id].paa[0], 0)
        self.assertEqual(imp_funcs.data[hazard][second_id].paa[8], 1)

        # general information
        self.assertEqual(imp_funcs.tag.file_name, ENT_DEMO_XLS)
        self.assertEqual(imp_funcs.tag.description, description)

    def test_template_file_pass(self):
        """ Read template excel file"""
        # Read demo excel file
        imp_funcs = ImpactFuncsExcel()
        imp_funcs.read(ENT_TEMPLATE_XLS)
        # Check some results
        self.assertEqual(len(imp_funcs.data), 10)
        self.assertEqual(len(imp_funcs.data['TC'][3].paa), 9)
        self.assertEqual(len(imp_funcs.data['EQ'][1].intensity), 14)
        self.assertEqual(len(imp_funcs.data['HS'][1].mdd), 16)

    def test_wrong_file_fail(self):
        """ Read file intensity, fail."""
        # Read demo excel file
        imp_funcs = ImpactFuncsExcel()
        imp_funcs.col_names['inten'] = 'wrong name'
        with self.assertRaises(KeyError):
            imp_funcs.read(ENT_DEMO_XLS)

# Execute TestReader
suite_reader = unittest.TestLoader().loadTestsFromTestCase(TestReader)
unittest.TextTestRunner(verbosity=2).run(suite_reader)
