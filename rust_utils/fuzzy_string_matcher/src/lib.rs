use pyo3::prelude::*;

/// Represents a word and its distance from a target word.
///
/// This struct holds both the word itself and its Damerau-Levenshtein distance
/// from a reference word. It can be unpacked in Python like a tuple.
///
/// Attributes:
///     word (str): The word being compared
///     distance (int): The Damerau-Levenshtein distance from the target word
#[pyclass]
#[derive(Clone)]
pub struct WordDistance {
    #[pyo3(get)]
    pub word: String,
    #[pyo3(get)]
    pub distance: usize,
}
#[pyclass]
struct Iter {
    word_distance: WordDistance,
    index: usize,
}
#[pymethods]
impl Iter {
    fn __iter__(slf: PyRef<'_, Self>) -> PyRef<'_, Self> {
        slf
    }
    fn __next__(mut slf: PyRefMut<'_, Self>) -> Option<PyObject> {
        if slf.index == 0 {
            slf.index += 1;
            Some(slf.word_distance.word.clone().into_py(slf.py()))
        } else if slf.index == 1 {
            slf.index += 1;
            Some(slf.word_distance.distance.into_py(slf.py()))
        } else {
            None
        }
    }
}

#[pymethods]
impl WordDistance {
    fn __iter__(slf: PyRef<'_, Self>) -> PyResult<Py<Iter>> {
        let iter = Iter {
            word_distance: slf.clone(),
            index: 0,
        };
        Py::new(slf.py(), iter)
    }
}


fn damerau_levenshtein(word1: &str, word2: &str) -> usize {
    let word1_len = word1.chars().count();
    let word2_len = word2.chars().count();

    let mut matrix = vec![vec![0; word2_len + 1]; word1_len + 1];

    for i in 0..=word1_len {
        matrix[i][0] = i;
    }
    for j in 0..=word2_len {
        matrix[0][j] = j;
    }

    for (i, char1) in word1.chars().enumerate() {
        for (j, char2) in word2.chars().enumerate() {
            let cost = if char1 == char2 { 0 } else { 1 };

            matrix[i + 1][j + 1] = std::cmp::min(
                matrix[i][j + 1] + 1,
                std::cmp::min(matrix[i + 1][j] + 1, matrix[i][j] + cost),
            );

            if i > 0
                && j > 0
                && char1 == word2.chars().nth(j - 1).unwrap()
                && char2 == word1.chars().nth(i - 1).unwrap()
            {
                matrix[i + 1][j + 1] =
                    std::cmp::min(matrix[i + 1][j + 1], matrix[i - 1][j - 1] + cost);
            }
        }
    }

    matrix[word1_len][word2_len]
}

/// Find the most similar words to a target word using Damerau-Levenshtein distance.
///
/// This function calculates the Damerau-Levenshtein edit distance between the target
/// word and each word in the provided list, then returns the N most similar matches
/// sorted by distance (lowest distance first).
///
/// Args:
///     obj_word (str): The target word to match against
///     word_list (list[str]): List of words to search through
///     num_results (int): Maximum number of results to return
///
/// Returns:
///     list[WordDistance]: List of WordDistance objects sorted by similarity (closest matches first)
///
/// Examples:
///     >>> find_most_similar_words("hello", ["helo", "world", "help"], 2)
///     [WordDistance(word="helo", distance=1), WordDistance(word="help", distance=2)]
#[pyfunction]
#[pyo3(signature = (obj_word, word_list, num_results))]
fn find_most_similar_words(
    obj_word: String,
    word_list: Vec<String>,
    num_results: usize,
) -> PyResult<Vec<WordDistance>> {
    let mut distances: Vec<WordDistance> = word_list
        .iter()
        .map(|word| {
            let distance = damerau_levenshtein(&obj_word, word);
            WordDistance {
                word: word.clone(),
                distance,
            }
        })
        .collect();

    distances.sort_by(|a, b| a.distance.cmp(&b.distance));
    distances.truncate(num_results);
    Ok(distances)
}


/// Fuzzy string matching module using Damerau-Levenshtein distance.
///
/// This module provides fast fuzzy string matching capabilities implemented in Rust.
/// It uses the Damerau-Levenshtein algorithm to calculate edit distances between strings,
/// accounting for insertions, deletions, substitutions, and transpositions.
///
/// Classes:
///     WordDistance: Container for a word and its distance from a target
///
/// Functions:
///     find_most_similar_words: Find N most similar words from a list
#[pymodule]
fn fuzzy_string_matcher(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_class::<WordDistance>()?;
    m.add_function(wrap_pyfunction!(find_most_similar_words, m)?)?;
    Ok(())
}
