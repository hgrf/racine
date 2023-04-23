import commonjs from '@rollup/plugin-commonjs';
import nodePolyfills from 'rollup-plugin-polyfill-node';
import nodeResolve from '@rollup/plugin-node-resolve';
// import json from '@rollup/plugin-json';
// import terser from '@rollup/plugin-terser';

export default {
  input: 'src/index.js',
  output: {
    format: 'iife',
    file: '../app/static/racine.js',
    name: 'R',
  },
  plugins: [
    commonjs({esmExternals: true}),
    nodePolyfills(),
    nodeResolve({browser: true}),
    // json(),
    // terser(),
  ],
};
