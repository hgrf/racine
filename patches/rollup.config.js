import nodePolyfills from 'rollup-plugin-polyfill-node';
import { nodeResolve } from '@rollup/plugin-node-resolve';
import commonjs from '@rollup/plugin-commonjs';
import json from '@rollup/plugin-json';
import terser from '@rollup/plugin-terser';

export default {
    input: 'src/index.js',
    output: {
        format: 'iife',
        file: '../../app/static/api-client.js',
        name: 'RacineApi',
    },
    plugins: [
        commonjs({esmExternals: true}),
        json(),
        nodePolyfills(),
        nodeResolve({browser: true}),
        terser(),
    ]
};
