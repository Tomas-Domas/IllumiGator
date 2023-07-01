use std::num::FpCategory::Nan;
use pyo3::prelude::*;
use nalgebra;
use nalgebra::{SMatrix, vector};

/// Formats the sum of two numbers as string.
#[pyfunction]
fn sum_as_string(a: usize, b: usize) -> PyResult<String> {
    Ok((a + b).to_string())
}

/// TODO: Implement line_line intersection in rust
/// Ray param is a nalgebra 2D vector containing two vectors of size 2.
/// Each vector contains 2, 32 bit floating points
/// Returns 1D vector with intersection point
fn get_line_line_intersection(ray: SMatrix<[f32; 2], 2, 1>) -> SMatrix<f32, 2, 1> {
    return SMatrix;
}

/// A Python module implemented in Rust.
#[pymodule]
fn illumiphysics(_py: Python, m: &PyModule) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(sum_as_string, m)?)?;
    Ok(())
}