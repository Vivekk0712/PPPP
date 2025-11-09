-- Quick fix for Skin Cancer Classifier project
-- Run this in Supabase SQL Editor

-- Option 1: Use general skin cancer keywords
UPDATE projects
SET search_keywords = ARRAY['skin', 'cancer', 'melanoma']
WHERE id = '237da916-d0cd-4350-96bb-7d49ab48b2da';

-- Option 2: Use specific popular dataset name
-- UPDATE projects
-- SET search_keywords = ARRAY['ham10000']
-- WHERE id = '237da916-d0cd-4350-96bb-7d49ab48b2da';

-- Option 3: Use ISIC dataset
-- UPDATE projects
-- SET search_keywords = ARRAY['isic', 'skin', 'lesion']
-- WHERE id = '237da916-d0cd-4350-96bb-7d49ab48b2da';

-- Verify the update
SELECT id, name, search_keywords, status
FROM projects
WHERE id = '237da916-d0cd-4350-96bb-7d49ab48b2da';
