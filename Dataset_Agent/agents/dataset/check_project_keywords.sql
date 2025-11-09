-- Check what search keywords are in your Skin Cancer project
SELECT 
    id,
    name,
    status,
    search_keywords,
    metadata
FROM projects
WHERE id = '237da916-d0cd-4350-96bb-7d49ab48b2da';

-- Update with better keywords for skin cancer datasets
UPDATE projects
SET search_keywords = ARRAY['skin', 'cancer', 'melanoma', 'dermatology']
WHERE id = '237da916-d0cd-4350-96bb-7d49ab48b2da';

-- Or use a specific dataset reference
-- UPDATE projects
-- SET search_keywords = ARRAY['skin-cancer-mnist-ham10000']
-- WHERE id = '237da916-d0cd-4350-96bb-7d49ab48b2da';
