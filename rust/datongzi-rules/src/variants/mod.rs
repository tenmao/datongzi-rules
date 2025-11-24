//! Game rule variants and configuration factory.
//!
//! This module provides pre-configured game setups and validation tools:
//! - `ConfigFactory`: Factory for creating common game configurations
//! - `VariantValidator`: Validator for checking configuration playability

mod config_factory;

pub use config_factory::{ConfigFactory, VariantValidator};
