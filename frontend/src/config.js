// config 파일은 root dir 에 위치해야 작동함
import { createMuiTheme } from '@material-ui/core/styles';

// material-ui custom global theme
export const theme = createMuiTheme ({
    overrides: {
        MuiCssBaseline: {
            "@global": {
                // 글로벌 스타일 정의
                body: {
                    fontSize: "20px",
                },
            },
        },
    },
});