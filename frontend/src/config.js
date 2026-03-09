/**
 * Application Configuration
 * Centralized API URLs and global settings
 */

export const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || '/api';
export const CAMERA_API_URL = import.meta.env.VITE_API_BASE_URL || '/api';

export const APP_CONFIG = {
  NAME: 'MEDIC1',
  TAGLINE: 'Chăm sóc sức khỏe người cao tuổi',
  VERSION: '2.0.0',
};

export default {
  API_BASE_URL,
  CAMERA_API_URL,
  APP_CONFIG,
};
