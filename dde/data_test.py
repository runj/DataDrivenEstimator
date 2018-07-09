#!/usr/bin/env python
# -*- coding:utf-8 -*-

import os
import shutil
import unittest

import dde
from dde.data import (get_data_from_db, prepare_folded_data, split_inner_val_from_train_data,
                      prepare_data_one_fold, prepare_folded_data_from_multiple_datasets,
                      prepare_full_train_data_from_multiple_datasets, split_test_from_train_and_val,
                      prepare_full_train_data_from_file, prepare_folded_data_from_file)


class TestData(unittest.TestCase):

    def setUp(self):

        X, y, _ = get_data_from_db('rmg', 'rmg_internal', 'kh_tricyclics_table')

        self.X = X
        self.y = y

    def test_get_HC_polycyclics_data_from_db(self):

        self.assertEqual(len(self.X), 180)
        self.assertEqual(len(self.y), 180)

    def test_get_data_from_db_using_Cp_data(self):

        X, y, _ = get_data_from_db('rmg', 'rmg_internal',
                                   'kh_tricyclics_table',
                                   prediction_task='Cp(cal/mol/K)')

        self.assertEqual(len(X), 180)
        self.assertEqual(len(y), 180)

    def test_prepare_folded_data(self):

        folds = 5
        shuffle_seed = 4
        X, y = self.X[:], self.y[:]  # Make copies because they get shuffled in place
        (folded_Xs, folded_ys) = prepare_folded_data(X, y, folds, shuffle_seed)
        self.assertEqual(len(folded_Xs), folds)
        self.assertEqual(len(folded_ys), folds)

        # test shuffle is expected
        import numpy as np
        all_indices = range(len(self.X))
        rng = np.random.RandomState(shuffle_seed)
        rng.shuffle(all_indices)

        first_X = folded_Xs[0][0]
        expected_first_X = self.X[all_indices[0]]

        self.assertTrue(np.all(np.equal(first_X, expected_first_X)))

    def test_split_inner_val_from_train_data(self):

        import numpy as np

        shuffle_seed = 4
        training_ratio = 0.9
        X, y = self.X[:], self.y[:]  # Make copies because they get shuffled in place
        data = split_inner_val_from_train_data(X, y, shuffle_seed, training_ratio)

        X_train = data[0]
        X_inner_val = data[1]

        self.assertAlmostEqual(len(X_train)*.1/len(X_inner_val), training_ratio, 1)

        # test shuffle is expected
        training_indices = range(len(self.X))
        rng = np.random.RandomState(shuffle_seed)
        rng.shuffle(training_indices)

        first_X_in_train = X_train[0]
        expected_first_X_in_train = self.X[training_indices[0]]

        self.assertTrue(np.all(np.equal(first_X_in_train, expected_first_X_in_train)))

    def test_prepare_data_one_fold(self):

        import numpy as np

        folds = 5
        training_ratio = 0.9

        n = len(self.X)
        target_fold_size = int(np.ceil(float(n) / folds))
        folded_Xs = [self.X[i:i+target_fold_size] for i in range(0, n, target_fold_size)]
        folded_ys = [self.y[i:i+target_fold_size] for i in range(0, n, target_fold_size)]

        shuffle_seed = 4  # seed for method `prepare_data_one_fold()`
        data = prepare_data_one_fold(folded_Xs, folded_ys, current_fold=0, training_ratio=training_ratio,
                                     shuffle_seed=shuffle_seed)

        self.assertEqual(len(data), 6)

        X_train = data[0]
        X_val = data[1]
        X_test = data[2]

        self.assertAlmostEqual(len(X_train)/10.0,
                               training_ratio*int(np.ceil(1.0*len(self.X)/folds))*(folds - 1)/10.0,
                               0)
        self.assertAlmostEqual(len(X_val)/10.0,
                               (1-training_ratio)*int(np.ceil(1.0*len(self.X)/folds))*(folds - 1)/10.0,
                               0)
        self.assertAlmostEqual(len(X_test)/10.0,
                               int(np.ceil(1.0*len(self.X)/folds))/10.0,
                               0)

        # test shuffle is expected
        testset_size = len(folded_Xs[0])
        training_val_indices = range(testset_size, len(self.X))
        rng = np.random.RandomState(shuffle_seed)
        rng.shuffle(training_val_indices)

        first_X_in_train = X_train[0]
        expected_first_X_in_train = self.X[training_val_indices[0]]

        self.assertTrue(np.all(np.equal(first_X_in_train, expected_first_X_in_train)))

    def test_prepare_folded_data_from_multiple_datasets(self):

        datasets = [
            ('rmg','rmg_internal', 'kh_tricyclics_table', 0.1),
            ('rmg','rmg_internal', 'kh_tricyclics_table', 0.1),
            ('rmg','rmg_internal', 'kh_tricyclics_table', 0.1)
        ]

        X_test, y_test, folded_Xs, folded_ys = prepare_folded_data_from_multiple_datasets(
                                        datasets=datasets,
                                        folds=5, add_extra_atom_attribute=True,
                                        add_extra_bond_attribute=True,
                                        differentiate_atom_type=True,
                                        differentiate_bond_type=True,
                                        prediction_task="Cp(cal/mol/K)")
        self.assertEqual(len(folded_Xs), 5)
        self.assertEqual(len(folded_ys), 5)

        self.assertEqual(len(X_test), 54)
        self.assertEqual(len(y_test), 54)
        self.assertEqual(len(folded_Xs[0]), 99)
        self.assertEqual(len(folded_Xs[0]), 99)

    def test_prepare_full_train_data_from_multiple_datasets(self):

        datasets = [
            ('rmg','rmg_internal', 'kh_tricyclics_table', 0.1),
            ('rmg','rmg_internal', 'kh_tricyclics_table', 0.1),
            ('rmg','rmg_internal', 'kh_tricyclics_table', 0.1)
        ]

        X_test, y_test, X_train, y_train = prepare_full_train_data_from_multiple_datasets(
                                                datasets=datasets,
                                                add_extra_atom_attribute=True,
                                                add_extra_bond_attribute=True,
                                                differentiate_atom_type=True,
                                                differentiate_bond_type=True,
                                                save_meta=False)
        self.assertEqual(len(X_train), 486)
        self.assertEqual(len(y_train), 486)

        self.assertEqual(len(X_test), 54)
        self.assertEqual(len(y_test), 54)

    def test_split_test_from_train_and_val(self):

        X_test, y_test, X_train_and_val, y_train_and_val = split_test_from_train_and_val(
                                                            self.X, self.y,
                                                            shuffle_seed=None,
                                                            testing_ratio=0.1)

        self.assertEqual(len(X_test), 18)
        self.assertEqual(len(y_test), 18)
        self.assertEqual(len(X_train_and_val), 162)
        self.assertEqual(len(y_train_and_val), 162)

    def test_prepare_full_train_data_from_file(self):
        datafile = os.path.join(os.path.dirname(dde.__file__),
                                'test_data',
                                'datafile.csv')
        tensors_dir = os.path.join(os.path.dirname(dde.__file__),
                                   'test_data',
                                   'tensors')

        X_test, y_test, X_train, y_train = prepare_full_train_data_from_file(
            datafile,
            add_extra_atom_attribute=True,
            add_extra_bond_attribute=True,
            differentiate_atom_type=True,
            differentiate_bond_type=True,
            save_meta=False,
            save_tensors_dir=tensors_dir,
            testing_ratio=0.0
        )

        self.assertTrue(os.path.exists(tensors_dir))
        self.assertTrue(all(os.path.exists(os.path.join(tensors_dir, '{}.npy'.format(i))) for i in range(10)))

        self.assertEqual(len(X_test), 0)
        self.assertEqual(len(y_test), 0)
        self.assertEqual(len(X_train), 10)
        self.assertEqual(len(y_train), 10)

        shutil.rmtree(tensors_dir)

    def test_prepare_folded_data_from_file(self):
        datafile = os.path.join(os.path.dirname(dde.__file__),
                                'test_data',
                                'datafile.csv')

        X_test, y_test, folded_Xs, folded_ys = prepare_folded_data_from_file(
            datafile, 5,
            add_extra_atom_attribute=True,
            add_extra_bond_attribute=True,
            differentiate_atom_type=True,
            differentiate_bond_type=True,
            testing_ratio=0.0
        )

        self.assertEqual(len(folded_Xs), 5)
        self.assertEqual(len(folded_ys), 5)

        self.assertEqual(len(X_test), 0)
        self.assertEqual(len(y_test), 0)
        self.assertEqual(len(folded_Xs[0]), 2)
        self.assertEqual(len(folded_ys[0]), 2)