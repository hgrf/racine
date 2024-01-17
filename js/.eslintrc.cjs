module.exports = {
  'env': {
    'browser': true,
    'es2021': true,
  },
  'extends': 'google',
  'overrides': [
  ],
  'parserOptions': {
    'ecmaVersion': 'latest',
    'sourceType': 'module',
  },
  'rules': {
    'require-jsdoc': 'off',
    'max-len': [
      'error',
      {
        "code": 100,
      }
    ],
    'no-undef': 'warn'
  },
  'ignorePatterns': [
    'src/api/**',
    'src/jquery-plugins/jquery.jeditable.js',
    'src/typeahead/**',
    'src/util/icons.js',
  ],
  'globals': {
    'CKEDITOR': 'readonly',
    'MathJax': 'readonly',
  },
};
