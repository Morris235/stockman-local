import { configure } from '@storybook/react';
// import requestContext from 'require-context.macro';

function loadStories() {
    require('../src/stories');
}

configure(loadStories, module);