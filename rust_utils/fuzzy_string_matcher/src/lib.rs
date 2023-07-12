use pyo3::prelude::*;

#[pyclass]
pub struct WordDistance {
    #[pyo3(get)]
    pub word: String,
    #[pyo3(get)]
    pub distance: usize,
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

#[pyfunction]
fn find_most_similar_words(
    obj_word: &str,
    word_list: Vec<&str>,
    num_results: usize,
) -> PyResult<Vec<WordDistance>> {
    let mut distances: Vec<WordDistance> = word_list
        .iter()
        .map(|word| {
            let distance = damerau_levenshtein(obj_word, word);
            WordDistance {
                word: word.to_string(),
                distance,
            }
        })
        .collect();

    distances.sort_by(|a, b| a.distance.cmp(&b.distance));
    distances.truncate(num_results);
    Ok(distances)
}


/// A Python module implemented in Rust. The name of this function must match
/// the `lib.name` setting in the `Cargo.toml`, else Python will not be able to
/// import the module.
#[pymodule]
fn fuzzy_string_matcher(_py: Python<'_>, m: &PyModule) -> PyResult<()> {
    m.add_class::<WordDistance>()?;
    m.add_function(wrap_pyfunction!(find_most_similar_words, m)?)?;
    Ok(())
}
