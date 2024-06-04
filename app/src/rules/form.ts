export function requiredField(value: string) {
    return !!value || 'Field is required'
}

export const requiredRule = [requiredField];
