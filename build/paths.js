const child_process = require('child_process');
const fs = require('fs');


/** Parses package.json */
const pkg = JSON.parse(fs.readFileSync('./package.json', 'utf-8'));

/** Src dir */
const sourcesRoot = 'src/' + pkg.name + '/';

/** "Main" static dir */
const staticRoot = sourcesRoot + 'static/';

// Find site packages (for includePaths).
const env = process.env.VIRTUAL_ENV || 'env';
let sitePackages;

try {
    python = child_process.execSync(`ls ${env}/lib`).toString().replace('\n', '');
    sitePackages = `${env}/lib/${python}/site-packages`;
} catch (e) {
    throw new Error('Please set VIRTUAL_ENV (or activate your environment).');
}

/**
 * Application path configuration for use in frontend scripts
 */
module.exports = {
    // Parsed package.json
    package: pkg,

    // Path to the scss entry point
    scssEntry: sourcesRoot + 'scss/screen.scss',

    // Path to the scss (sources) directory
    scssSrcDir: sourcesRoot + 'scss/',

    // Path to the js entry point (source)
    jsEntry: sourcesRoot + 'js/index.js',

    // Path to js (sources)
    jsSrc: sourcesRoot + 'js/**/*.js',

    // Path to the js (sources) directory
    jsSrcDir: sourcesRoot + 'js/',

    // Path to the (transpiled) js directory
    jsDir: staticRoot + 'bundles/',

    // Path to js spec (test) files
    jsSpec: sourcesRoot + 'jstests/**/*.spec.js',

    // Path to js spec (test) entry file
    jsSpecEntry: sourcesRoot + 'jstests/index.js',

    // Path to js code coverage directory
    coverageDir: 'reports/jstests/',

    sitePackages: sitePackages,
};
