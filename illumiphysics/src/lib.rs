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
fn get_line_line_intersection(ray_x: SMatrix<[f32; 2], 2, 1>) -> SMatrix<f32, 2, 1> {
    return SMatrix;
}

/// A Python module implemented in Rust.
#[pymodule]
fn illumiphysics(_py: Python, m: &PyModule) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(sum_as_string, m)?)?;
    Ok(())
}