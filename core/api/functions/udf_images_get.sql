-- DROP FUNCTION IF EXISTS public.udf_images_get(integer);
CREATE OR REPLACE FUNCTION public.udf_images_get(
    param_spot_id integer)
  RETURNS character varying AS
$BODY$

DECLARE

  json_returning json = '[]';
    
  BEGIN        

  /*
  -- To Test:
    SELECT udf_images_get(1);
  */

  IF EXISTS (
    SELECT
      si.id
    FROM public.site_imageses si
      INNER JOIN public.spots s
        ON si.spot_id = s.id
        AND
        si.is_active
        AND
        not si.is_deleted                      
        AND
        s.is_active
        AND
        not s.is_deleted
        AND
        s.id = param_spot_id
    ) THEN

      -- RAISE NOTICE 'Were found images of the current place';

      SELECT JSON_AGG(a.*) INTO STRICT json_returning as "imageList"
      FROM (
        SELECT
          si.id "imageId",
          si.uri "imageURI",
          si.extension,
          si.principalimage,
          si.is_active
        FROM public.api_images si
          INNER JOIN public.api_spots s
            ON si.spot_id = s.id
            AND
            si.is_active
            AND
            not si.is_deleted                      
            AND
            s.is_active
            AND
            not s.is_deleted
            AND
            s.id = param_spot_id
        GROUP BY
          si.id, si.spot_id
        ORDER BY 
          si.id, si.principalimage
      )a;

  ELSE

    RAISE NOTICE 'Were not found images of the current place';

  END IF;

    RETURN '"imageList":' || json_returning;

END;

$BODY$
  LANGUAGE plpgsql VOLATILE
  COST 100;
ALTER FUNCTION public.udf_images_get(integer)
  OWNER TO postgres;