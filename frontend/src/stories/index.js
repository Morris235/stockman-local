import React from 'react';
import { storiesOf } from '@storybook/react';

import { BoardInput } from '../UI/atoms/BoardInputForm';
import { CounterButton } from '../UI/atoms/Button';

storiesOf('BoaderInput Component', module)
.add('First setting', () => <BoardInput name='name' />);

storiesOf('Button function', module)
.add('nextPreButton', () => <CounterButton name='name' />);