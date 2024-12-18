import { useState, useCallback } from 'react';

export const useForm = (initialValues = {}, validate) => {
  const [values, setValues] = useState(initialValues);
  const [errors, setErrors] = useState({});
  const [touched, setTouched] = useState({});

  const handleChange = useCallback((e) => {
    const { name, value } = e.target;
    setValues(prev => ({ ...prev, [name]: value }));
    if (touched[name] && validate) {
      const validationErrors = validate({ ...values, [name]: value });
      setErrors(validationErrors);
    }
  }, [values, touched, validate]);

  const handleBlur = useCallback((e) => {
    const { name } = e.target;
    setTouched(prev => ({ ...prev, [name]: true }));
    if (validate) {
      const validationErrors = validate(values);
      setErrors(validationErrors);
    }
  }, [values, validate]);

  const handleSubmit = useCallback((onSubmit) => async (e) => {
    e.preventDefault();
    if (validate) {
      const validationErrors = validate(values);
      setErrors(validationErrors);
      if (Object.keys(validationErrors).length > 0) {
        return;
      }
    }
    await onSubmit(values);
  }, [values, validate]);

  return {
    values,
    errors,
    touched,
    handleChange,
    handleBlur,
    handleSubmit,
    setValues
  };
};