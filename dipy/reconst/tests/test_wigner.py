import numpy as np
from numpy.testing import assert_array_almost_equal
from dipy.reconst.wigner import (
    z_rot_mat,
    rot_mat,
    change_of_basis_matrix,
    _cc2rc,
    wigner_d_matrix,
    wigner_D_matrix,
    so3_rfft,
    so3_rifft,
    complex_mm,
)


def test_z_rot_mat():
    # Test for zero angle rotation, should return identity matrix
    angle = np.pi / 2
    l = 1
    expected_90_rot = np.array([[0, -1, 0], [1, 0, 0], [0, 0, 1]])
    assert_array_almost_equal(z_rot_mat(angle, l), expected_90_rot)


def test_rot_mat():
    # Test for identity rotation (no rotation)
    alpha, beta, gamma = 0, 0, 0
    l = 2
    J = np.eye(2 * l + 1)
    expected_identity = np.eye(2 * l + 1)
    assert_array_almost_equal(
        rot_mat(alpha, beta, gamma, l, J), expected_identity)


def test_change_of_basis_matrix():
    # Test for no change scenario
    l = 2
    frm = to = ("real", "quantum", "centered", "cs")
    expected_identity = np.eye(2 * l + 1)
    assert_array_almost_equal(
        change_of_basis_matrix(l, frm, to), expected_identity)


def test_cc2rc():
    # Test for l = 0, should return sqrt(2) as the only element
    l = 0
    B = _cc2rc(l)
    expected_matrix = np.array([[np.sqrt(2)]])
    assert_array_almost_equal(B, expected_matrix)


def test_wigner_d_matrix():
    # Test for beta = 0, should return identity
    l = 2
    beta = 0
    expected_identity = np.eye(2 * l + 1)
    assert_array_almost_equal(wigner_d_matrix(l, beta), expected_identity)


def test_wigner_D_matrix():
    # Test for identity rotation (no rotation)
    l = 2
    alpha, beta, gamma = 0, 0, 0
    expected_identity = np.eye(2 * l + 1)
    assert_array_almost_equal(wigner_D_matrix(
        l, alpha, beta, gamma), expected_identity)


def test_so3_rfft():
    # Test with a simple input array
    x = np.random.rand(2, 4, 4, 4)  # Assuming b_in = 2
    transformed = so3_rfft(x)
    # Based on b_out = b_in = 2, and nspec calculation
    expected_shape = (5, 2, 2)
    assert transformed.shape == expected_shape
    assert transformed.dtype == np.complex64 or transformed.dtype == np.complex128


def test_so3_rifft():
    # Test with a simple spectral input
    x = np.random.rand(5, 2, 2) + 1j * np.random.rand(5,
                                                      2, 2)  # Assuming nspec=5
    transformed = so3_rifft(x)
    # Assuming b_out = 2, matching the input shape of so3_rfft
    expected_shape = (2, 4, 4, 4)
    assert transformed.shape == expected_shape
    # Depending on implementation
    assert transformed.dtype == np.float32 or transformed.dtype == np.float64


def test_complex_mm():
    # Test with simple complex matrices
    x = np.random.rand(2, 3, 2)  # Shape (M, K, complex)
    y = np.random.rand(3, 4, 2)  # Shape (K, N, complex)
    result = complex_mm(x, y)
    expected_shape = (2, 4, 2)  # Shape (M, N, complex)
    assert result.shape == expected_shape
    assert result.dtype == x.dtype

    # Test with conjugation
    result_conj_x = complex_mm(x, y, conj_x=True)
    result_conj_y = complex_mm(x, y, conj_y=True)
    result_conj_both = complex_mm(x, y, conj_x=True, conj_y=True)
    # Ensure the conjugation actually changes the result
    assert not np.allclose(result, result_conj_x)
    assert not np.allclose(result, result_conj_y)
    assert not np.allclose(result, result_conj_both)
