import { Button, type ButtonProps } from 'antd'

const AppButton = (props: ButtonProps) => {
    return (
        <Button
            type="primary"
            size="large"
            {...props}
        />
    )
}

export default AppButton
